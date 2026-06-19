import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def after_migrate():
	create_tactix_roles()
	create_custom_fields(get_custom_fields(), ignore_validate=True)


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