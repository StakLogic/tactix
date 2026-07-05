import frappe
import json

def resolve_db_folder(path):
	"""
	Resolves an explorer path (e.g. '/Clients/Google/Reports__1234') to its standard Frappe database folder record name.
	Dynamically creates missing parent directories in the standard system if they do not exist.
	"""
	if not path or path == "/":
		return "Home"

	parts = [p for p in path.split("/") if p]
	current_parent = "Home"

	for part in parts:
		# Inherit attachments target from parent folder
		parent_doc = frappe.db.get_value("File", current_parent, ["attached_to_doctype", "attached_to_name"], as_dict=True) or {}
		attached_doctype = parent_doc.get("attached_to_doctype")
		attached_name = parent_doc.get("attached_to_name")

		# Override at top-level category mappings
		if current_parent == "Home/Clients":
			attached_doctype = "Tactix Customer"
			attached_name = part
		elif current_parent == "Home/Departments":
			attached_doctype = "Tactix Department"
			attached_name = part
		elif current_parent == "Home" and part == "Shared":
			attached_doctype = "User"
			attached_name = "Administrator"

		child_name = f"{current_parent}/{part}"

		if not frappe.db.exists("File", child_name):
			folder_doc = frappe.get_doc({
				"doctype": "File",
				"file_name": part,
				"is_folder": 1,
				"folder": current_parent,
				"attached_to_doctype": attached_doctype,
				"attached_to_name": attached_name,
				"is_private": 0
			})
			folder_doc.insert(ignore_permissions=True)

		current_parent = child_name

	return current_parent


def parse_explorer_path(path):
	if not path or path == "":
		return None, None, "/"
	path = path.strip()
	doctype = None
	docname = None
	relative_path = "/"

	if path == "/Shared" or path.startswith("/Shared/"):
		doctype = "User"
		docname = "Administrator"
		relative_path = path[len("/Shared"):] or "/"
	elif path.startswith("/Clients/"):
		parts = [p for p in path.split("/") if p]
		if len(parts) >= 2:
			customer_name = parts[1]
			doctype = "Tactix Customer"
			docname = customer_name
			relative_path = "/" + "/".join(parts[2:]) if len(parts) > 2 else "/"
	elif path.startswith("/Departments/"):
		parts = [p for p in path.split("/") if p]
		if len(parts) >= 2:
			dept_name = parts[1]
			doctype = "Tactix Department"
			docname = dept_name
			relative_path = "/" + "/".join(parts[2:]) if len(parts) > 2 else "/"
	return doctype, docname, relative_path


@frappe.whitelist()
def get_folder_contents(path="/"):
	user = frappe.session.user
	roles = frappe.get_roles(user)
	is_admin = "System Manager" in roles
	is_ticket_raiser = "Tactix Ticket Raiser" in roles and not is_admin

	user_details = frappe.db.get_value(
		"User", user, ["tactix_customer"], as_dict=True
	) or {}
	user_customer = user_details.get("tactix_customer")

	if is_ticket_raiser:
		if not user_customer:
			return {"folders": [], "files": [], "current_path": "/"}
		if path == "/" or not path.startswith(f"/Clients/{user_customer}"):
			path = f"/Clients/{user_customer}"

	if not path or path == "":
		path = "/"
	path = path.strip()

	folders = []
	files = []

	doctype, docname, relative_path = parse_explorer_path(path)

	if path == "/":
		folders.append({"name": "Shared", "is_folder": True, "path": "/Shared"})
		if not is_ticket_raiser:
			folders.append({"name": "Clients", "is_folder": True, "path": "/Clients"})
			folders.append({"name": "Departments", "is_folder": True, "path": "/Departments"})
		else:
			folders.append({"name": user_customer, "is_folder": True, "path": f"/Clients/{user_customer}"})

	elif path == "/Clients":
		if is_ticket_raiser:
			folders.append({"name": user_customer, "is_folder": True, "path": f"/Clients/{user_customer}"})
		else:
			customers = frappe.db.get_all("Tactix Customer", fields=["name"])
			for cust in customers:
				folders.append({"name": cust.name, "is_folder": True, "path": f"/Clients/{cust.name}"})

	elif path == "/Departments":
		if is_ticket_raiser:
			frappe.throw("Not permitted to view departments.", frappe.PermissionError)
		else:
			departments = frappe.db.get_all("Tactix Department", fields=["name"])
			for dept in departments:
				folders.append({"name": dept.name, "is_folder": True, "path": f"/Departments/{dept.name}"})

	else:
		if path.startswith("/Clients/"):
			customer_name = path[len("/Clients/"):].split("/")[0]
			if not frappe.db.exists("Tactix Customer", customer_name):
				frappe.throw(f"Customer {customer_name} does not exist.")
			if is_ticket_raiser and customer_name != user_customer:
				frappe.throw("Not permitted to view these files.", frappe.PermissionError)
		elif path.startswith("/Departments/"):
			dept_name = path[len("/Departments/"):].split("/")[0]
			if not frappe.db.exists("Tactix Department", dept_name):
				frappe.throw(f"Department {dept_name} does not exist.")
			if is_ticket_raiser:
				frappe.throw("Not permitted to view departments.", frappe.PermissionError)

		db_folder = resolve_db_folder(path)

		# Query folders inside standard parent folder
		subfolders_db = frappe.db.get_all(
			"File",
			filters={
				"is_folder": 1,
				"folder": db_folder
			},
			fields=["file_name"]
		)
		for sf in subfolders_db:
			p_suffix = "" if path.endswith("/") else "/"
			display_name = sf.file_name.split("__")[0] if "__" in sf.file_name else sf.file_name
			folders.append({
				"name": display_name,
				"is_folder": True,
				"path": f"{path}{p_suffix}{sf.file_name}"
			})

		# Query files inside standard parent folder
		files_db = frappe.db.get_all(
			"File",
			filters={
				"is_folder": 0,
				"folder": db_folder
			},
			fields=["name", "file_name", "file_url", "file_size", "creation", "owner"]
		)
		for f in files_db:
			f["source"] = "Direct" if path.startswith("/Clients") or path.startswith("/Departments") else "Shared"
			f["source_name"] = path.split("/")[2] if len(path.split("/")) > 2 else ""

		# Aggregate Ticket and Task files only at root level of customer/department
		ticket_files = []
		task_files = []
		parts = [p for p in path.split("/") if p]
		if len(parts) == 2:
			parent_cat = parts[0]
			docname = parts[1]

			if parent_cat == "Clients":
				tickets = frappe.db.get_all("Tactix Ticket", filters={"customer": docname}, pluck="name")
				if tickets:
					ticket_files = frappe.db.get_all(
						"File",
						filters={"attached_to_doctype": "Tactix Ticket", "attached_to_name": ["in", tickets]},
						fields=["name", "file_name", "file_url", "file_size", "creation", "owner", "attached_to_name"]
					)
					for f in ticket_files:
						f["source"] = "Ticket"
						f["source_name"] = f.get("attached_to_name")
					
					tasks = frappe.db.get_all("Task", filters={"tactix_ticket": ["in", tickets]}, pluck="name")
					if tasks:
						task_files = frappe.db.get_all(
							"File",
							filters={"attached_to_doctype": "Task", "attached_to_name": ["in", tasks]},
							fields=["name", "file_name", "file_url", "file_size", "creation", "owner", "attached_to_name"]
						)
						for f in task_files:
							task_subject = frappe.db.get_value("Task", f.get("attached_to_name"), "subject")
							f["source"] = "Task"
							f["source_name"] = f.get("attached_to_name")
							f["task_subject"] = task_subject or f.get("attached_to_name")
			elif parent_cat == "Departments":
				tickets = frappe.db.get_all("Tactix Ticket", filters={"department": docname}, pluck="name")
				if tickets:
					ticket_files = frappe.db.get_all(
						"File",
						filters={"attached_to_doctype": "Tactix Ticket", "attached_to_name": ["in", tickets]},
						fields=["name", "file_name", "file_url", "file_size", "creation", "owner", "attached_to_name"]
					)
					for f in ticket_files:
						f["source"] = "Ticket"
						f["source_name"] = f.get("attached_to_name")

				tasks = frappe.db.get_all("Task", filters={"department": docname}, pluck="name")
				if tasks:
					task_files = frappe.db.get_all(
						"File",
						filters={"attached_to_doctype": "Task", "attached_to_name": ["in", tasks]},
						fields=["name", "file_name", "file_url", "file_size", "creation", "owner", "attached_to_name"]
					)
					for f in task_files:
						task_subject = frappe.db.get_value("Task", f.get("attached_to_name"), "subject")
						f["source"] = "Task"
						f["source_name"] = f.get("attached_to_name")
						f["task_subject"] = task_subject or f.get("attached_to_name")

		files = files_db + ticket_files + task_files

	files.sort(key=lambda x: x.get("creation") or "", reverse=True)

	for f in files:
		owner_name = frappe.db.get_value("User", f.get("owner"), "full_name")
		f["owner_full_name"] = owner_name or f.get("owner")
		f["owner_image"] = frappe.db.get_value("User", f.get("owner"), "user_image") or ""

	# Also return standard DB folder name
	db_folder = resolve_db_folder(path)

	return {
		"folders": folders,
		"files": files,
		"current_path": path,
		"db_folder": db_folder
	}


@frappe.whitelist()
def delete_explorer_file(file_name):
	user = frappe.session.user
	roles = frappe.get_roles(user)
	is_admin = "System Manager" in roles
	is_ticket_raiser = "Tactix Ticket Raiser" in roles and not is_admin

	if not frappe.db.exists("File", file_name):
		frappe.throw("File not found.")

	file_doc = frappe.get_doc("File", file_name)

	if is_ticket_raiser:
		user_details = frappe.db.get_value("User", user, ["tactix_customer"], as_dict=True) or {}
		user_customer = user_details.get("tactix_customer")
		if not user_customer:
			frappe.throw("Not permitted.", frappe.PermissionError)

		allowed = False
		if file_doc.owner == user or (file_doc.attached_to_doctype == "Tactix Customer" and file_doc.attached_to_name == user_customer):
			allowed = True

		if not allowed:
			frappe.throw("Not permitted to delete this file.", frappe.PermissionError)

	file_doc.delete()
	return {"success": True}


@frappe.whitelist()
def create_explorer_folder(path, folder_name):
	user = frappe.session.user
	roles = frappe.get_roles(user)
	is_admin = "System Manager" in roles
	is_ticket_raiser = "Tactix Ticket Raiser" in roles and not is_admin

	user_details = frappe.db.get_value("User", user, ["tactix_customer"], as_dict=True) or {}
	user_customer = user_details.get("tactix_customer")

	if is_ticket_raiser:
		if not user_customer:
			frappe.throw("Not permitted.", frappe.PermissionError)
		if not path.startswith(f"/Clients/{user_customer}"):
			frappe.throw("Not permitted.", frappe.PermissionError)

	db_parent = resolve_db_folder(path)

	# Inherit attachments target
	parent_doc = frappe.get_doc("File", db_parent)
	attached_doctype = parent_doc.attached_to_doctype
	attached_name = parent_doc.attached_to_name

	unique_id = frappe.generate_hash(length=8)
	db_folder_name = f"{folder_name.strip()}__{unique_id}"

	folder_doc = frappe.get_doc({
		"doctype": "File",
		"file_name": db_folder_name,
		"is_folder": 1,
		"folder": db_parent,
		"attached_to_doctype": attached_doctype,
		"attached_to_name": attached_name,
		"is_private": 0
	})
	folder_doc.insert(ignore_permissions=True)
	return {"success": True}
