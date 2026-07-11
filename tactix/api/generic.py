import frappe
import json

@frappe.whitelist()
def get_user_info():
	user = frappe.session.user
	roles = frappe.get_roles(user)
	is_admin = "System Manager" in roles
	is_ticket_raiser = "Tactix Ticket Raiser" in roles and not is_admin

	user_details = frappe.db.get_value(
		"User", user, ["tactix_customer", "tactix_department", "user_image"], 
		as_dict=1
	)
	is_department_head = False
	if user_details.get("tactix_department"):
		if frappe.get_value("Tactix Department", {
			"name": user_details.get("tactix_department"), "department_head": user}, 
			"department_head"
		):
			is_department_head = True

	return {
		"admin": is_admin,
		"is_ticket_raiser": is_ticket_raiser,
		"tactix_customer": user_details.get("tactix_customer"),
		"tactix_department": user_details.get("tactix_department"),
		"is_department_head": is_department_head,
		"user_image": user_details.get("user_image"),
		"roles": roles
	}


@frappe.whitelist()
def get_users_excluding_ticket_users():
	# Get all users and their roles
	users_roles = frappe.db.get_all(
		"Has Role",
		filters={"parenttype": "User"},
		fields=["parent", "role"]
	)
	
	# Group roles by user
	user_roles_map = {}
	for d in users_roles:
		user_roles_map.setdefault(d.parent, []).append(d.role)
	
	exclude_users = ["Administrator", "Guest"]
	for user, roles in user_roles_map.items():
		if "Tactix Ticket Raiser" in roles and not ("System Manager" in roles or "Employee" in roles):
			exclude_users.append(user)

	# Also exclude if they have a customer assigned
	customer_users = [
		d.name for d in frappe.db.get_all(
			"User",
			filters={"tactix_customer": ["is", "set"]},
			fields=["name"]
		)
	]
	exclude_users = list(set(exclude_users + customer_users))

	users = frappe.db.get_all(
		"User",
		filters={
			"enabled": 1,
			"name": ["not in", exclude_users]
		},
		fields=["name", "full_name", "user_image"]
	)
	return users


from werkzeug.exceptions import HTTPException
from werkzeug.utils import redirect as wz_redirect

class RedirectException(HTTPException):
	def __init__(self, location, code=302):
		super().__init__()
		self.response = wz_redirect(location, code=code)


def restrict_desk_access():
	if not frappe.request:
		return

	path = frappe.request.path or ""
	if path.startswith("/app") or path == "/app":
		if frappe.session.user != "Guest":
			roles = frappe.get_roles(frappe.session.user)
			if "System Manager" not in roles:
				raise RedirectException("/tactix/?restricted=1")