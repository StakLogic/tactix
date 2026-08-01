import frappe
from frappe import _

@frappe.whitelist()
def get_master_records(doctype):
	roles = frappe.get_roles(frappe.session.user)
	if "System Manager" not in roles:
		frappe.throw(_("Not authorized to read master records."))
		
	if doctype not in ["Project", "Department", "Tactix Department", "Tactix Customer", "Tactix Team"]:
		frappe.throw(_("Invalid DocType."))
		
	if doctype == "Project":
		return frappe.get_list(doctype, fields=["name", "project_name", "company", "expected_end_date"])
	elif doctype == "Department":
		return frappe.get_list(doctype, fields=["name", "department_name", "company", "parent_department"])
	elif doctype == "Tactix Department":
		return frappe.get_list(doctype, fields=["name", "department_name", "department_head"])
	elif doctype == "Tactix Customer":
		return frappe.get_list(doctype, fields=["name"])
	elif doctype == "Tactix Team":
		return frappe.get_list(doctype, fields=["name", "team_name", "team_lead", "description"])

@frappe.whitelist()
def create_master_record(doctype, doc_data):
	roles = frappe.get_roles(frappe.session.user)
	if "System Manager" not in roles:
		frappe.throw(_("Not authorized to write master records."))
		
	if doctype not in ["Project", "Department", "Tactix Department", "Tactix Customer", "Tactix Team"]:
		frappe.throw(_("Invalid DocType."))
		
	data = frappe.parse_json(doc_data)
	
	if doctype == "Project":
		doc = frappe.get_doc({
			"doctype": "Project",
			"project_name": data.get("project_name"),
			"company": data.get("company") or "SUPER AI",
			"naming_series": "PROJ-.####"
		})
	elif doctype == "Department":
		doc = frappe.get_doc({
			"doctype": "Department",
			"department_name": data.get("department_name"),
			"company": data.get("company") or "SUPER AI"
		})
	elif doctype == "Tactix Department":
		doc = frappe.get_doc({
			"doctype": "Tactix Department",
			"department_name": data.get("department_name"),
			"department_head": data.get("department_head")
		})
	elif doctype == "Tactix Customer":
		doc = frappe.get_doc({
			"doctype": "Tactix Customer",
			"name": data.get("name")
		})
	elif doctype == "Tactix Team":
		doc = frappe.get_doc({
			"doctype": "Tactix Team",
			"team_name": data.get("team_name"),
			"team_lead": data.get("team_lead"),
			"description": data.get("description")
		})
		
	doc.insert()
	frappe.db.commit()
	return {"status": "success", "name": doc.name}

@frappe.whitelist()
def update_master_record(doctype, name, doc_data):
	roles = frappe.get_roles(frappe.session.user)
	if "System Manager" not in roles:
		frappe.throw(_("Not authorized to write master records."))
		
	if doctype not in ["Project", "Department", "Tactix Department", "Tactix Customer", "Tactix Team"]:
		frappe.throw(_("Invalid DocType."))
		
	data = frappe.parse_json(doc_data)
	doc = frappe.get_doc(doctype, name)
	
	if doctype == "Project":
		doc.project_name = data.get("project_name")
		if data.get("company"):
			doc.company = data.get("company")
	elif doctype == "Department":
		doc.department_name = data.get("department_name")
		if data.get("company"):
			doc.company = data.get("company")
	elif doctype == "Tactix Department":
		doc.department_name = data.get("department_name")
		doc.department_head = data.get("department_head")
	elif doctype == "Tactix Customer":
		# Tactix Customer's primary key is name, which can be renamed if allowed
		pass
	elif doctype == "Tactix Team":
		doc.team_name = data.get("team_name")
		doc.team_lead = data.get("team_lead")
		doc.description = data.get("description")
		
	doc.save()
	frappe.db.commit()
	return {"status": "success"}

@frappe.whitelist()
def delete_master_record(doctype, name):
	roles = frappe.get_roles(frappe.session.user)
	if "System Manager" not in roles:
		frappe.throw(_("Not authorized to delete master records."))
		
	if doctype not in ["Project", "Department", "Tactix Department", "Tactix Customer", "Tactix Team"]:
		frappe.throw(_("Invalid DocType."))
		
	frappe.delete_doc(doctype, name)
	frappe.db.commit()
	return {"status": "success"}

@frappe.whitelist()
def get_link_options():
	return {
		"companies": frappe.db.get_all("Company", pluck="name"),
		"users": frappe.db.get_all("User", filters={"enabled": 1}, pluck="name")
	}
