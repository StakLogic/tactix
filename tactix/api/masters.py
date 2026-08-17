import frappe
from frappe import _
from tactix.api.generic import get_default_company

@frappe.whitelist()
def get_master_records(doctype):
	roles = frappe.get_roles(frappe.session.user)
	if "System Manager" not in roles:
		frappe.throw(_("Not authorized to read master records."))
		
	if doctype not in ["Project", "Department", "Tactix Customer", "Tactix Team"]:
		frappe.throw(_("Invalid DocType."))
		
	if doctype == "Project":
		return frappe.get_list(doctype, fields=["name", "project_name", "company", "expected_end_date"])
	elif doctype == "Department":
		return frappe.get_list(doctype, fields=["name", "department_name", "company", "parent_department"])
	elif doctype == "Tactix Customer":
		return frappe.get_list(doctype, fields=["name"])
	elif doctype == "Tactix Team":
		teams = frappe.get_list(doctype, fields=["name", "team_name", "team_lead", "description"])
		for t in teams:
			try:
				doc = frappe.get_doc("Tactix Team", t.name)
				t["members"] = [m.user for m in doc.get("members", [])]
			except Exception:
				t["members"] = []
		return teams

@frappe.whitelist()
def save_master_record(action, doctype, name=None, data=None):
	if action == "create":
		return create_master_record(doctype, data)
	elif action == "update":
		return update_master_record(doctype, name, data)
	elif action == "delete":
		return delete_master_record(doctype, name)
	else:
		frappe.throw(_("Invalid action"))

@frappe.whitelist()
def create_master_record(doctype, doc_data):
	roles = frappe.get_roles(frappe.session.user)
	if "System Manager" not in roles:
		frappe.throw(_("Not authorized to write master records."))
		
	if doctype not in ["Project", "Department", "Tactix Customer", "Tactix Team"]:
		frappe.throw(_("Invalid DocType."))
		
	data = frappe.parse_json(doc_data) if isinstance(doc_data, str) else (doc_data or {})
	
	if doctype == "Project":
		doc = frappe.get_doc({
			"doctype": "Project",
			"project_name": data.get("project_name"),
			"company": data.get("company") or get_default_company(),
			"naming_series": "PROJ-.####"
		})
	elif doctype == "Department":
		doc = frappe.get_doc({
			"doctype": "Department",
			"department_name": data.get("department_name"),
			"company": data.get("company") or get_default_company()
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
			"team_lead": data.get("team_lead") or None,
			"description": data.get("description") or None
		})
		if data.get("members"):
			for u in data.get("members"):
				val = u.get("value") if isinstance(u, dict) else u
				if val:
					doc.append("members", {"user": val})
		
	doc.insert()
	frappe.db.commit()
	return {"status": "success", "name": doc.name}

@frappe.whitelist()
def update_master_record(doctype, name, doc_data):
	roles = frappe.get_roles(frappe.session.user)
	if "System Manager" not in roles:
		frappe.throw(_("Not authorized to write master records."))
		
	if doctype not in ["Project", "Department", "Tactix Customer", "Tactix Team"]:
		frappe.throw(_("Invalid DocType."))
		
	data = frappe.parse_json(doc_data) if isinstance(doc_data, str) else (doc_data or {})
	doc = frappe.get_doc(doctype, name)
	
	if doctype == "Project":
		doc.project_name = data.get("project_name")
		if data.get("company"):
			doc.company = data.get("company")
	elif doctype == "Department":
		doc.department_name = data.get("department_name")
		if data.get("company"):
			doc.company = data.get("company")
	elif doctype == "Tactix Customer":
		pass
	elif doctype == "Tactix Team":
		doc.team_name = data.get("team_name")
		doc.team_lead = data.get("team_lead") or None
		doc.description = data.get("description") or None
		doc.set("members", [])
		if data.get("members"):
			for u in data.get("members"):
				val = u.get("value") if isinstance(u, dict) else u
				if val:
					doc.append("members", {"user": val})
		
	doc.save()
	frappe.db.commit()
	return {"status": "success"}

@frappe.whitelist()
def delete_master_record(doctype, name):
	roles = frappe.get_roles(frappe.session.user)
	if "System Manager" not in roles:
		frappe.throw(_("Not authorized to delete master records."))
		
	if doctype not in ["Project", "Department", "Tactix Customer", "Tactix Team"]:
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
