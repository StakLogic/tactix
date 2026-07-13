import frappe
from frappe import _
import json
from frappe.utils import get_datetime, add_to_date, today, flt

@frappe.whitelist()
def get_employee_info():
	"""Get Employee linked to current user."""
	user = frappe.session.user
	employee = frappe.db.get_value("Employee", {"user_id": user}, ["name", "employee_name"], as_dict=True)
	if not employee:
		employee = frappe.db.get_value("Employee", {"prefered_email": user}, ["name", "employee_name"], as_dict=True)
	if not employee:
		employee = frappe.db.get_value("Employee", {"personal_email": user}, ["name", "employee_name"], as_dict=True)
	
	info = dict(employee or {})
	info["has_submit_permission"] = frappe.has_permission("Timesheet", "submit")
	info["is_system_manager"] = "System Manager" in frappe.get_roles(user)
	return info

@frappe.whitelist()
def get_employees():
	"""Get list of active employees for System Manager select dropdown."""
	roles = frappe.get_roles(frappe.session.user)
	if "System Manager" not in roles:
		frappe.throw(_("Not authorized to load employee list."))
	
	employees = frappe.get_all("Employee", filters={"status": "Active"}, fields=["name", "employee_name"])
	return [{"label": f"{e.employee_name} ({e.name})", "value": e.name} for e in employees]

@frappe.whitelist()
def get_tasks_options():
	"""Get list of Tasks for Timesheet dropdown."""
	user = frappe.session.user
	roles = frappe.get_roles(user)
	
	filters = {}
	or_filters = None
	
	if "Employee" in roles and "System Manager" not in roles:
		assigned_tasks = frappe.db.get_all("Task Assigned To", {"user": user}, pluck="parent") or [""]
		or_filters = [
			["name", "in", assigned_tasks],
			["owner", "=", user],
			["assigned_by", "=", user]
		]
		
	tasks = frappe.get_all("Task", filters=filters, or_filters=or_filters, fields=["name", "subject", "project"])
	
	return [{"label": f"{t.subject} ({t.name})", "value": t.name, "project": t.project} for t in tasks]

def _normalize_timesheet_filters(filters):
	if isinstance(filters, str):
		filters = json.loads(filters)
	filters = dict(filters or {})
	
	timespan = filters.pop("timespan", None)
	if timespan:
		from frappe.utils import today, add_days, getdate
		import datetime
		
		today_date = getdate(today())
		if timespan == "today":
			filters["start_date"] = today()
		elif timespan == "yesterday":
			filters["start_date"] = add_days(today(), -1)
		elif timespan == "this_week":
			start_of_week = today_date - datetime.timedelta(days=today_date.weekday())
			filters["start_date"] = [">=", start_of_week.strftime("%Y-%m-%d")]
		elif timespan == "last_week":
			start_of_last_week = today_date - datetime.timedelta(days=today_date.weekday() + 7)
			end_of_last_week = start_of_last_week + datetime.timedelta(days=6)
			filters["start_date"] = ["between", [start_of_last_week.strftime("%Y-%m-%d"), end_of_last_week.strftime("%Y-%m-%d")]]
		elif timespan == "this_month":
			start_of_month = today_date.replace(day=1)
			filters["start_date"] = [">=", start_of_month.strftime("%Y-%m-%d")]
		elif timespan == "last_month":
			first_day_this_month = today_date.replace(day=1)
			end_of_last_month = first_day_this_month - datetime.timedelta(days=1)
			start_of_last_month = end_of_last_month.replace(day=1)
			filters["start_date"] = ["between", [start_of_last_month.strftime("%Y-%m-%d"), end_of_last_month.strftime("%Y-%m-%d")]]
			
	return filters

@frappe.whitelist()
def get_timesheets(filters=None, start=0, page_length=20):
	"""Get list of Timesheets."""
	filters = _normalize_timesheet_filters(filters)
	
	user = frappe.session.user
	roles = frappe.get_roles(user)
	
	# Authorization validation: Employees can only view their own timesheets
	if "Employee" in roles and "System Manager" not in roles:
		employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
		if employee:
			filters["employee"] = employee
		else:
			filters["owner"] = user

	total_count = len(frappe.get_list("Timesheet", filters=filters, fields=["name"]))
	
	timesheets = frappe.get_list(
		"Timesheet",
		filters=filters,
		fields=["name", "start_date", "employee", "employee_name", "total_hours", "status", "creation"],
		order_by="creation desc",
		limit_start=int(start),
		limit_page_length=int(page_length)
	)
	
	return {
		"timesheets": timesheets,
		"total_count": total_count
	}

@frappe.whitelist()
def get_timesheet_summary(filters=None):
	"""Get aggregated totals for timesheet stats cards."""
	filters = _normalize_timesheet_filters(filters)
	
	user = frappe.session.user
	roles = frappe.get_roles(user)
	
	# Authorization validation
	if "Employee" in roles and "System Manager" not in roles:
		employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
		if employee:
			filters["employee"] = employee
		else:
			filters["owner"] = user
			
	timesheets = frappe.get_list("Timesheet", filters=filters, fields=["total_hours", "status", "start_date"])
	
	total_hours = sum(flt(t.total_hours) for t in timesheets)
	submitted_count = sum(1 for t in timesheets if t.status == "Submitted")
	draft_count = sum(1 for t in timesheets if t.status == "Draft")
	active_days = len(set(t.start_date for t in timesheets if t.start_date))
	
	return {
		"total_hours": total_hours,
		"submitted_count": submitted_count,
		"draft_count": draft_count,
		"active_days": active_days
	}

@frappe.whitelist()
def create_timesheet(doc):
	"""Create and optionally submit a Timesheet document."""
	if isinstance(doc, str):
		doc = json.loads(doc)
		
	user = frappe.session.user
	roles = frappe.get_roles(user)
	employee_info = get_employee_info()
	
	# Authorization: non-admin users must only log under their own employee record
	if "System Manager" not in roles:
		employee = employee_info.get("name")
		if not employee:
			frappe.throw(_("No employee profile linked to your user account. Please contact your system administrator."))
	else:
		employee = doc.get("employee") or employee_info.get("name")
		if not employee:
			frappe.throw(_("Please select an employee."))

	date = doc.get("date") or today()
	company = frappe.db.get_value("Employee", employee, "company") or frappe.defaults.get_user_default("company") or frappe.db.get_single_value("Global Defaults", "default_company")
	
	timesheet = frappe.new_doc("Timesheet")
	timesheet.employee = employee
	timesheet.employee_name = employee_info.get("employee_name") or frappe.db.get_value("Employee", employee, "employee_name")
	timesheet.company = company
	timesheet.start_date = date
	timesheet.end_date = date
	
	base_time = get_datetime(f"{date} 09:00:00")
	
	time_logs = doc.get("time_logs") or []
	if not time_logs:
		frappe.throw(_("Timesheet must have at least one task entry."))
		
	total_hours = 0.0
	for entry in time_logs:
		hours = flt(entry.get("hours"))
		if hours <= 0:
			frappe.throw(_("Hours for each task must be greater than zero."))
			
		to_time = add_to_date(base_time, hours=hours)
		
		row = timesheet.append("time_logs", {})
		row.activity_type = entry.get("activity_type") or "Execution"
		row.from_time = base_time
		row.to_time = to_time
		row.hours = hours
		row.project = entry.get("project")
		row.task = entry.get("task")
		row.description = entry.get("description") or ""
		row.is_billable = entry.get("is_billable") or 0
		
		if row.is_billable:
			billing_rate = flt(entry.get("billing_rate")) or flt(frappe.db.get_value("Activity Type", row.activity_type, "billing_rate"))
			row.billing_rate = billing_rate
			row.billing_amount = billing_rate * hours
			
		base_time = to_time
		total_hours += hours
		
	timesheet.total_hours = total_hours
	
	timesheet.insert()
	
	if doc.get("submit"):
		timesheet.submit()
		
	return timesheet.name

@frappe.whitelist()
def get_timesheet_detail(name):
	"""Get detailed Timesheet document with resolved task subjects."""
	timesheet = frappe.get_doc("Timesheet", name)
	frappe.has_permission("Timesheet", "read", timesheet, throw=True)
	
	doc_dict = timesheet.as_dict()
	
	# Resolve task subjects
	for row in doc_dict.get("time_logs") or []:
		if row.get("task"):
			row["task_subject"] = frappe.db.get_value("Task", row.get("task"), "subject")
			
	doc_dict["has_submit_permission"] = frappe.has_permission("Timesheet", "submit", doc=timesheet)
	return doc_dict

@frappe.whitelist()
def edit_timesheet(name, doc):
	"""Update an existing Timesheet document."""
	if isinstance(doc, str):
		doc = json.loads(doc)
		
	timesheet = frappe.get_doc("Timesheet", name)
	frappe.has_permission("Timesheet", "write", timesheet, throw=True)
	
	if timesheet.docstatus != 0:
		frappe.throw(_("Submitted Timesheets cannot be edited."))
		
	timesheet.start_date = doc.get("date")
	timesheet.end_date = doc.get("date")
	
	timesheet.set("time_logs", [])
	
	base_time = get_datetime(f"{doc.get('date')} 09:00:00")
	total_hours = 0.0
	
	for entry in doc.get("time_logs") or []:
		hours = flt(entry.get("hours"))
		if hours <= 0:
			frappe.throw(_("Hours for each task must be greater than zero."))
			
		to_time = add_to_date(base_time, hours=hours)
		
		row = timesheet.append("time_logs", {})
		row.activity_type = entry.get("activity_type") or "Execution"
		row.from_time = base_time
		row.to_time = to_time
		row.hours = hours
		row.project = entry.get("project")
		row.task = entry.get("task")
		row.description = entry.get("description") or ""
		row.is_billable = entry.get("is_billable") or 0
		
		if row.is_billable:
			billing_rate = flt(entry.get("billing_rate")) or flt(frappe.db.get_value("Activity Type", row.activity_type, "billing_rate"))
			row.billing_rate = billing_rate
			row.billing_amount = billing_rate * hours
			
		base_time = to_time
		total_hours += hours
		
	timesheet.total_hours = total_hours
	timesheet.save(ignore_permissions=True)
	
	if doc.get("submit"):
		timesheet.submit()
		
	return timesheet.name
