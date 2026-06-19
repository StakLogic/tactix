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
		"user_image": user_details.get("user_image")
	}


@frappe.whitelist()
def get_upcoming_leaves(from_date=None, to_date=None):
	from frappe.utils import getdate, add_days

	today_val = getdate()
	
	if from_date:
		start_val = getdate(from_date)
	else:
		start_val = today_val

	if to_date:
		end_val = getdate(to_date)
	else:
		end_val = add_days(start_val, 7)

	leaves = frappe.db.get_all(
		"Tactix Leave Application",
		filters={
			"status": ["in", ["Approved", "Pending"]],
			"from_date": ["<=", end_val],
			"to_date": [">=", start_val]
		},
		fields=["name", "user", "from_date", "to_date", "remarks", "posting_date", "status"],
		order_by="from_date asc"
	)

	for leave in leaves:
		user_details = frappe.db.get_value("User", leave.user, ["full_name", "user_image"], as_dict=True) or {}
		leave["full_name"] = user_details.get("full_name") or leave.user
		leave["user_image"] = user_details.get("user_image") or ""

	return leaves

