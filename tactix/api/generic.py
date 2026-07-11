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


