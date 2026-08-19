import frappe
from frappe import _
from tactix.api.generic import get_default_company

@frappe.whitelist()
def get_users_data():
	roles = frappe.get_roles(frappe.session.user)
	if "System Manager" not in roles:
		frappe.throw(_("Not authorized to manage users."))
		
	# 1. Fetch users
	users = frappe.get_all("User", 
		fields=["name", "email", "first_name", "last_name", "enabled", "user_image", "tactix_customer"],
		filters={"name": ["not in", ["Administrator", "Guest"]]}
	)
	
	# 2. Fetch role assignments
	user_roles = frappe.get_all("Has Role", filters={"parenttype": "User"}, fields=["parent", "role"])
	roles_by_user = {}
	for ur in user_roles:
		roles_by_user.setdefault(ur.parent, []).append(ur.role)
		
	# 3. Fetch employee mappings (departments)
	employees = frappe.get_all("Employee", fields=["user_id", "department", "name", "gender", "date_of_birth", "date_of_joining", "github_username"])
	emp_by_user = {e.user_id: e for e in employees if e.user_id}
	
	# Assemble user list
	user_list = []
	for u in users:
		uid = u.name
		emp_info = emp_by_user.get(uid, {})
		user_list.append({
			"email": u.email,
			"first_name": u.first_name,
			"last_name": u.last_name,
			"enabled": u.enabled,
			"user_image": u.user_image,
			"tactix_customer": u.tactix_customer or "",
			"roles": roles_by_user.get(uid, []),
			"department": emp_info.get("department") or "",
			"employee_id": emp_info.get("name") or "",
			"gender": emp_info.get("gender") or "",
			"date_of_birth": str(emp_info.get("date_of_birth")) if emp_info.get("date_of_birth") else "",
			"date_of_joining": str(emp_info.get("date_of_joining")) if emp_info.get("date_of_joining") else "",
			"github_username": emp_info.get("github_username") or ""
		})
		
	# 4. Fetch all active roles
	all_roles = [r.name for r in frappe.get_all("Role", fields=["name"]) if not r.name.startswith("All") and r.name not in ["Guest", "Administrator"]]
	
	# 5. Fetch departments list
	depts = [d.name for d in frappe.get_all("Department", fields=["name"])]
	
	# 6. Fetch customers list
	customers = [c.name for c in frappe.get_all("Tactix Customer", fields=["name"])]
	
	return {
		"users": user_list,
		"roles": all_roles,
		"departments": depts,
		"customers": customers
	}

import re

def get_clean_error_message(e):
	raw = ""
	if getattr(frappe, "message_log", None):
		msg = frappe.message_log[-1]
		if isinstance(msg, dict):
			raw = msg.get("message", "")
		else:
			raw = str(msg)
	if not raw:
		raw = str(e)
	clean = re.sub(r"<[^>]+>", " ", raw)
	clean = " ".join(clean.split())
	return clean or str(e)


@frappe.whitelist()
def save_user(email, doc_data):
	roles = frappe.get_roles(frappe.session.user)
	if "System Manager" not in roles:
		frappe.throw(_("Not authorized to manage users."))
		
	data = frappe.parse_json(doc_data)
	is_new = not email
	
	first_name = data.get("first_name")
	last_name = data.get("last_name") or ""
	enabled = data.get("enabled", 1)
	roles_list = data.get("roles", [])
	department = data.get("department")
	password = data.get("password")
	tactix_customer = data.get("tactix_customer")
	
	gender = data.get("gender")
	date_of_birth = data.get("date_of_birth")
	date_of_joining = data.get("date_of_joining")
	github_username = data.get("github_username")
	
	is_ticket_raiser = "Tactix Ticket Raiser" in roles_list
	
	try:
		if is_new:
			target_email = data.get("email")
			if not target_email:
				frappe.throw(_("Email is required for new users."))
			if frappe.db.exists("User", target_email):
				frappe.throw(_("User with email {0} already exists.").format(target_email))
				
			user_doc = frappe.get_doc({
				"doctype": "User",
				"email": target_email,
				"first_name": first_name,
				"last_name": last_name,
				"enabled": enabled,
				"send_welcome_email": 0,
				"tactix_customer": tactix_customer if is_ticket_raiser else "",
				"roles": [{"role": r} for r in roles_list]
			})
			if password:
				user_doc.new_password = password
			user_doc.insert()
			
			# Create corresponding Employee only if not a Ticket Raiser
			if not is_ticket_raiser:
				if not gender or not date_of_birth or not date_of_joining:
					frappe.throw(_("Gender, Date of Birth, and Date of Joining are mandatory for employees."))
				emp_doc = frappe.get_doc({
					"doctype": "Employee",
					"user_id": target_email,
					"first_name": first_name,
					"last_name": last_name,
					"employee_name": f"{first_name} {last_name}".strip(),
					"company": data.get("company") or get_default_company(),
					"department": department,
					"status": "Active",
					"gender": gender,
					"date_of_birth": date_of_birth,
					"date_of_joining": date_of_joining,
					"github_username": github_username
				})
				emp_doc.insert()
			
		else:
			target_email = email
			user_doc = frappe.get_doc("User", target_email)
			user_doc.first_name = first_name
			user_doc.last_name = last_name
			user_doc.enabled = enabled
			user_doc.tactix_customer = tactix_customer if is_ticket_raiser else ""
			if password:
				user_doc.new_password = password
				
			# Update Roles
			user_doc.set("roles", [])
			for r in roles_list:
				user_doc.append("roles", {"role": r})
			user_doc.save()
			
			# Update corresponding Employee
			emp_names = frappe.db.get_all("Employee", filters={"user_id": target_email}, pluck="name")
			if not is_ticket_raiser:
				if not gender or not date_of_birth or not date_of_joining:
					frappe.throw(_("Gender, Date of Birth, and Date of Joining are mandatory for employees."))
				if emp_names:
					emp_doc = frappe.get_doc("Employee", emp_names[0])
					emp_doc.first_name = first_name
					emp_doc.last_name = last_name
					emp_doc.employee_name = f"{first_name} {last_name}".strip()
					if data.get("company"):
						emp_doc.company = data.get("company")
					emp_doc.department = department
					emp_doc.gender = gender
					emp_doc.date_of_birth = date_of_birth
					emp_doc.date_of_joining = date_of_joining
					emp_doc.github_username = github_username
					emp_doc.save()
				else:
					emp_doc = frappe.get_doc({
						"doctype": "Employee",
						"user_id": target_email,
						"first_name": first_name,
						"last_name": last_name,
						"employee_name": f"{first_name} {last_name}".strip(),
						"company": data.get("company") or get_default_company(),
						"department": department,
						"status": "Active",
						"gender": gender,
						"date_of_birth": date_of_birth,
						"date_of_joining": date_of_joining,
						"github_username": github_username
					})
					emp_doc.insert()
			else:
				# If the user has a Ticket Raiser role, delete their Employee document if it exists
				for emp in emp_names:
					frappe.delete_doc("Employee", emp, force=1, ignore_permissions=True)
				
		frappe.db.commit()
		return {"status": "success", "email": target_email}

	except Exception as e:
		frappe.db.rollback()
		return {"status": "error", "error": get_clean_error_message(e)}

@frappe.whitelist()
def delete_user(email):
	roles = frappe.get_roles(frappe.session.user)
	if "System Manager" not in roles:
		frappe.throw(_("Not authorized to manage users."))
		
	if not email or email in ["Administrator", "Guest"]:
		frappe.throw(_("Cannot delete system user."))

	try:
		# 1. Delete associated User Permissions for target email
		user_perms = frappe.get_all("User Permission", filters={"user": email}, pluck="name")
		for up in user_perms:
			frappe.delete_doc("User Permission", up, force=1, ignore_permissions=True)

		# 2. Delete corresponding Employee doc(s) & employee permissions
		emp_names = frappe.db.get_all("Employee", filters={"user_id": email}, pluck="name")
		for emp in emp_names:
			emp_perms = frappe.get_all("User Permission", filters={"allow": "Employee", "for_value": emp}, pluck="name")
			for ep in emp_perms:
				frappe.delete_doc("User Permission", ep, force=1, ignore_permissions=True)
			frappe.delete_doc("Employee", emp, force=1, ignore_permissions=True)

		# 3. Delete User doc
		frappe.delete_doc("User", email, force=1, ignore_permissions=True)
		frappe.db.commit()
		return {"status": "success"}

	except Exception as e:
		frappe.db.rollback()
		return {"status": "error", "error": get_clean_error_message(e)}


