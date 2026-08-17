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
		frappe.throw("Access Restricted: Drive is exclusively for internal organization staff.", frappe.PermissionError)

	if not path or path == "":
		path = "/"
	path = path.strip()

	folders = []
	files = []

	doctype, docname, relative_path = parse_explorer_path(path)

	if path == "/":
		folders.append({"name": "Shared", "is_folder": True, "path": "/Shared"})
		folders.append({"name": "Clients", "is_folder": True, "path": "/Clients"})

	elif path == "/Clients":
		if is_ticket_raiser:
			if user_customer:
				folders.append({"name": user_customer, "is_folder": True, "path": f"/Clients/{user_customer}"})
		else:
			customers = frappe.db.get_all("Tactix Customer", fields=["name"])
			for cust in customers:
				folders.append({"name": cust.name, "is_folder": True, "path": f"/Clients/{cust.name}"})

	else:
		if path.startswith("/Clients/"):
			customer_name = path[len("/Clients/"):].split("/")[0]
			if not frappe.db.exists("Tactix Customer", customer_name):
				frappe.throw(f"Customer {customer_name} does not exist.")
			if is_ticket_raiser and customer_name != user_customer:
				frappe.throw("Not permitted to view these files.", frappe.PermissionError)

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

		files = files_db + ticket_files + task_files

	files.sort(key=lambda x: x.get("creation") or "", reverse=True)

	for f in files:
		owner_name = frappe.db.get_value("User", f.get("owner"), "full_name")
		f["owner_full_name"] = owner_name or f.get("owner")
		f["owner_image"] = frappe.db.get_value("User", f.get("owner"), "user_image") or ""

	# Query shares for files for current user
	user_shares = frappe.db.get_all(
		"DocShare",
		filters={"share_doctype": "File", "user": user},
		fields=["share_name", "read", "write"]
	)
	shared_file_map = {s.share_name: s for s in user_shares}

	for f in files:
		file_id = f.get("name")
		file_owner = f.get("owner")
		
		# Get share count for file
		shares = frappe.db.get_all(
			"DocShare",
			filters={"share_doctype": "File", "share_name": file_id},
			fields=["user", "read", "write"]
		)
		
		owner_name = frappe.db.get_value("User", file_owner, "full_name")
		f["owner_full_name"] = owner_name or file_owner
		f["owner_image"] = frappe.db.get_value("User", file_owner, "user_image") or ""
		f["is_owner"] = (file_owner == user)
		f["can_share"] = is_admin or (file_owner == user)
		f["shares_count"] = len(shares)
		f["is_shared"] = len(shares) > 0
		f["shared_with_me"] = file_id in shared_file_map
		
		# Determine permission level
		if is_admin or file_owner == user:
			f["permission"] = "write"
		elif file_id in shared_file_map:
			f["permission"] = "write" if shared_file_map[file_id].write else "read"
		else:
			f["permission"] = "read"

	# Access control filtering for non-admin internal staff (Employees, Team Leads, Code Reviewers)
	if not is_admin and not is_ticket_raiser:
		# User is internal staff (Employee / Developer, Team Lead, Code Reviewer)
		accessible_files = []
		for f in files:
			file_id = f.get("name")
			file_owner = f.get("owner")
			
			# Allowed conditions:
			# 1. User owns the file
			# 2. File is explicitly shared with the user via DocShare
			# 3. File is in the public company /Shared folder
			# 4. File is attached to a ticket/task where user is involved
			if file_owner == user or file_id in shared_file_map or path.startswith("/Shared"):
				accessible_files.append(f)
			elif f.get("source") in ["Ticket", "Task"]:
				accessible_files.append(f)
		
		files = accessible_files

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

	# Check permissions: Admin or Owner or write share
	if not is_admin:
		if file_doc.owner != user:
			has_write_share = frappe.db.exists("DocShare", {
				"share_doctype": "File",
				"share_name": file_name,
				"user": user,
				"write": 1
			})
			if not has_write_share:
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


@frappe.whitelist()
def get_shareable_users():
	"""
	Returns list of internal users (excluding Guest, Administrator, and Ticket Raisers)
	available for file sharing, along with their roles (Admin, Team Lead, Code Reviewer, Developer/Employee).
	"""
	user_roles = frappe.get_all("Has Role", filters={"parenttype": "User"}, fields=["parent", "role"])
	roles_by_user = {}
	for ur in user_roles:
		roles_by_user.setdefault(ur.parent, []).append(ur.role)

	users = frappe.db.get_all(
		"User",
		filters={"enabled": 1, "name": ["not in", ["Administrator", "Guest"]]},
		fields=["name", "email", "full_name", "user_image", "tactix_customer"]
	)

	result = []
	for u in users:
		# Exclude pure Ticket Raisers with customer assigned
		roles = roles_by_user.get(u.name, [])
		if "Tactix Ticket Raiser" in roles and not ("System Manager" in roles or "Employee" in roles):
			continue
		if u.tactix_customer:
			continue

		# Determine primary role display badge
		primary_role = "Employee"
		if "System Manager" in roles:
			primary_role = "Admin"
		elif "Team Lead" in roles:
			primary_role = "Team Lead"
		elif "Code Reviewer" in roles:
			primary_role = "Code Reviewer"
		elif "Developer" in roles:
			primary_role = "Developer"
		elif "Employee" in roles:
			primary_role = "Developer"

		result.append({
			"name": u.name,
			"email": u.email,
			"full_name": u.full_name or u.email,
			"user_image": u.user_image or "",
			"primary_role": primary_role,
			"roles": roles
		})

	return result


@frappe.whitelist()
def get_file_shares(file_name):
	"""
	Returns user share details for a specific file.
	"""
	if not frappe.db.exists("File", file_name):
		frappe.throw("File not found.")

	file_doc = frappe.db.get_value("File", file_name, ["name", "file_name", "owner"], as_dict=True)
	owner_details = frappe.db.get_value("User", file_doc.owner, ["name", "email", "full_name", "user_image"], as_dict=True) or {}

	shares = frappe.get_all(
		"DocShare",
		filters={"share_doctype": "File", "share_name": file_name},
		fields=["name", "user", "read", "write"]
	)

	user_roles = frappe.get_all("Has Role", filters={"parenttype": "User"}, fields=["parent", "role"])
	roles_by_user = {}
	for ur in user_roles:
		roles_by_user.setdefault(ur.parent, []).append(ur.role)

	share_list = []
	for s in shares:
		u_info = frappe.db.get_value("User", s.user, ["full_name", "email", "user_image"], as_dict=True) or {}
		u_roles = roles_by_user.get(s.user, [])
		
		primary_role = "Employee"
		if "System Manager" in u_roles:
			primary_role = "Admin"
		elif "Team Lead" in u_roles:
			primary_role = "Team Lead"
		elif "Code Reviewer" in u_roles:
			primary_role = "Code Reviewer"
		elif "Developer" in u_roles or "Employee" in u_roles:
			primary_role = "Developer"

		share_list.append({
			"share_id": s.name,
			"user": s.user,
			"full_name": u_info.get("full_name") or s.user,
			"email": u_info.get("email") or s.user,
			"user_image": u_info.get("user_image") or "",
			"primary_role": primary_role,
			"read": s.read,
			"write": s.write,
			"permission": "write" if s.write else "read"
		})

	return {
		"file_name": file_doc.file_name,
		"owner": {
			"user": file_doc.owner,
			"full_name": owner_details.get("full_name") or file_doc.owner,
			"email": owner_details.get("email") or file_doc.owner,
			"user_image": owner_details.get("user_image") or ""
		},
		"shares": share_list
	}


@frappe.whitelist()
def share_file(file_name, target_user, permission="read"):
	"""
	Shares a file with a target user, giving read or write permission, and sends a notification.
	"""
	user = frappe.session.user
	roles = frappe.get_roles(user)
	is_admin = "System Manager" in roles

	if not frappe.db.exists("File", file_name):
		frappe.throw("File not found.")

	file_doc = frappe.get_doc("File", file_name)

	# Only admin or file owner can share
	if not is_admin and file_doc.owner != user:
		frappe.throw("Only file owner or admin can share this file.", frappe.PermissionError)

	write_access = 1 if permission == "write" else 0

	# Frappe share add
	frappe.share.add("File", file_name, target_user, read=1, write=write_access, notify=0)

	# Send notification
	from tactix.api.generic import create_notification_log
	sharer_name = frappe.db.get_value("User", user, "full_name") or user
	subject = f"File shared with you: '{file_doc.file_name}' by {sharer_name}"
	try:
		create_notification_log(
			for_user=target_user,
			subject=subject,
			document_type="File",
			document_name=file_name,
			from_user=user
		)
	except Exception:
		pass

	return {"success": True, "message": f"Shared file with {target_user}"}


@frappe.whitelist()
def unshare_file(file_name, target_user):
	"""
	Revokes file sharing for a target user.
	"""
	user = frappe.session.user
	roles = frappe.get_roles(user)
	is_admin = "System Manager" in roles

	if not frappe.db.exists("File", file_name):
		frappe.throw("File not found.")

	file_doc = frappe.get_doc("File", file_name)

	# Only admin or file owner can unshare
	if not is_admin and file_doc.owner != user:
		frappe.throw("Only file owner or admin can update sharing.", frappe.PermissionError)

	frappe.share.remove("File", file_name, target_user)
	return {"success": True, "message": f"Revoked access for {target_user}"}


@frappe.whitelist()
def share_multiple_files(file_names, target_user, permission="read"):
	"""
	Shares multiple files with a target user.
	"""
	if isinstance(file_names, str):
		file_names = json.loads(file_names)

	for fname in file_names:
		if frappe.db.exists("File", fname):
			share_file(fname, target_user, permission)

	return {"success": True, "count": len(file_names)}


@frappe.whitelist()
def delete_multiple_files(file_names):
	"""
	Deletes multiple files.
	"""
	if isinstance(file_names, str):
		file_names = json.loads(file_names)

	for fname in file_names:
		if frappe.db.exists("File", fname):
			delete_explorer_file(fname)

	return {"success": True, "count": len(file_names)}


