import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def after_migrate():
	create_tactix_roles()
	create_custom_fields(get_custom_fields(), ignore_validate=True)
	setup_role_permissions()


def setup_role_permissions():
	# System Manager Permissions
	for doctype in [
		"Task", "Project", "Tactix Ticket", "Tactix Customer", "Tactix Department",
		"Task Assigned To", "Tactix Ticket Attachment", "Github Settings",
		"Tactix Pull Request"
	]:
		grant_custom_permission(doctype, "System Manager", {
			"read": 1, "write": 1, "create": 1, "delete": 1,
			"share": 1, "export": 1, "print": 1, "email": 1,
			"report": 1, "if_owner": 0
		})

	# Employee Permissions
	grant_custom_permission("Task", "Employee", {
		"read": 1, "write": 1, "create": 1, "delete": 1,
		"share": 1, "export": 1, "print": 1, "email": 1,
		"report": 1, "if_owner": 0  # Only If Creator (handles assignment and creation access)
	})

	grant_custom_permission("Tactix Ticket", "Employee", {
		"read": 1, "write": 1, "create": 1, "delete": 1,
		"share": 1, "export": 1, "print": 1, "email": 1,
		"report": 1, "if_owner": 0  # Only If Creator / Assigned
	})

	grant_custom_permission("Project", "Employee", {
		"read": 1, "write": 0, "create": 0, "delete": 0,
		"share": 1, "export": 0, "print": 1, "email": 1,
		"report": 1, "if_owner": 0
	})

	grant_custom_permission("Tactix Customer", "Employee", {
		"read": 1, "write": 0, "create": 0, "delete": 0,
		"share": 1, "export": 0, "print": 1, "email": 1,
		"report": 1, "if_owner": 0
	})

	grant_custom_permission("Tactix Department", "Employee", {
		"read": 1, "write": 0, "create": 0, "delete": 0,
		"share": 1, "export": 0, "print": 1, "email": 1,
		"report": 1, "if_owner": 0
	})


	# Ticket User
	grant_custom_permission("Tactix Ticket", "Tactix Ticket Raiser", {
		"read": 1, "write": 1, "create": 1,
	})

	grant_custom_permission("Tactix Customer", "Tactix Ticket Raiser", {
		"read": 1, "write": 1, "create": 1,
	})

	grant_custom_permission("Tactix Department", "Tactix Ticket Raiser", {
		"read": 1, "write": 1, "create": 1,
	})


def grant_custom_permission(doctype, role, perm_dict):
	if not frappe.db.exists("Custom DocPerm", {"parent": doctype, "role": role}):
		doc = frappe.get_doc({
			"doctype": "Custom DocPerm",
			"parent": doctype,
			"parenttype": "DocType",
			"parentfield": "permissions",
			"role": role,
			"permlevel": 0,
			**perm_dict
		})
		doc.insert(ignore_permissions=True)
	else:
		# Update existing Custom DocPerm if it exists
		docname = frappe.db.get_value("Custom DocPerm", {"parent": doctype, "role": role}, "name")
		if docname:
			doc = frappe.get_doc("Custom DocPerm", docname)
			doc.update(perm_dict)
			doc.save(ignore_permissions=True)
	
	frappe.clear_cache(doctype=doctype)


def create_tactix_roles():
	role_name = "Tactix Ticket Raiser"

	if not frappe.db.exists("Role", role_name):
		role = frappe.get_doc({
			"doctype": "Role",
			"role_name": role_name,
		})
		role.insert(ignore_permissions=True)


def get_custom_fields():
	return {
		"Task":[
			{
				"fieldname": "assigned_by",
				"label": "Assigned By",
				"fieldtype":"Link",
				"options":"User",
				"insert_after":"parent_task",
			},
			{
				"fieldname": "assigned_to_users",
				"label": "Assigned To",
				"fieldtype":"Table MultiSelect",
				"options":"Task Assigned To",
				"insert_after":"assigned_by",
			},
			{
				"fieldname": "assigned_datetime",
				"label": "Assigned Date",
				"fieldtype":"Datetime",
				"insert_after":"exp_start_date",
			},
			{
				"fieldname": "completed_datetime",
				"label": "Completed Date",
				"fieldtype":"Datetime",
				"insert_after":"exp_end_date",
			},
			{
				"fieldname": "fullfilled_in",
				"label": "Fullfilled In (mins)",
				"fieldtype":"Float",
				"insert_after":"assigned_to",
			},
			{
				"fieldname": "fullfilled_in_display_text",
				"label": "Fullfilled In Text",
				"fieldtype":"Data",
				"insert_after":"fullfilled_in",
				"read_only": 1
			},
			{
				"fieldname": "department",
				"label": "Department",
				"fieldtype":"Link",
				"options":"Department",
				"insert_after":"project",
				"read_only": 1
			},
			{
				"fieldname": "is_overdue",
				"label": "Is Overdue",
				"fieldtype":"Check",
				"insert_after":"is_template",
			},
			{
				"fieldname": "tactix_ticket",
				"label": "Tactix Ticket",
				"fieldtype":"Link",
				"options":"Tactix Ticket",
				"insert_after":"color",
			},
			{
				"fieldname": "security_impact",
				"label": "Security Impact",
				"fieldtype": "Select",
				"options": "\nYes\nNo\nNot Applicable",
				"insert_after": "tactix_ticket",
			}
		],
		"User":[
			{
				"fieldname": "tactix_customer",
				"label": "Oper Customer",
				"fieldtype":"Link",
				"options":"Tactix Customer",
				"insert_after":"mobile_no",
			},
			{
				"fieldname": "tactix_department",
				"label": "Tactix Department",
				"fieldtype":"Link",
				"options":"Tactix Department",
				"insert_after":"tactix_customer",
			},
		]
	}