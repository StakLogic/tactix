import frappe
from frappe import _
import json
from frappe.utils import today, add_days, getdate, flt
import datetime

def _normalize_timespan(timespan):
	today_date = getdate(today())
	start_date = None
	end_date = today()
	
	if timespan == "today":
		start_date = today()
	elif timespan == "yesterday":
		start_date = add_days(today(), -1)
		end_date = add_days(today(), -1)
	elif timespan == "this_week":
		start_date = (today_date - datetime.timedelta(days=today_date.weekday())).strftime("%Y-%m-%d")
	elif timespan == "last_week":
		start_date = (today_date - datetime.timedelta(days=today_date.weekday() + 7)).strftime("%Y-%m-%d")
		end_date = (today_date - datetime.timedelta(days=today_date.weekday() + 1)).strftime("%Y-%m-%d")
	elif timespan == "this_month":
		start_date = today_date.replace(day=1).strftime("%Y-%m-%d")
	elif timespan == "last_month":
		first_day_this_month = today_date.replace(day=1)
		end_date_dt = first_day_this_month - datetime.timedelta(days=1)
		start_date = end_date_dt.replace(day=1).strftime("%Y-%m-%d")
		end_date = end_date_dt.strftime("%Y-%m-%d")
	elif timespan == "this_year":
		start_date = today_date.replace(month=1, day=1).strftime("%Y-%m-%d")
		
	return start_date, end_date

@frappe.whitelist()
def get_performance_data(employee=None, timespan=None):
	"""Get compiled metrics and breakdowns for Performance Dashboard."""
	user = frappe.session.user
	roles = frappe.get_roles(user)
	
	# Authorization & role boundaries enforcement
	if "Employee" in roles and "System Manager" not in roles:
		employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
		if not employee:
			return {}
			
	start_date, end_date = _normalize_timespan(timespan)
	
	# Resolve Employee User ID if filtering
	employee_user_id = None
	if employee:
		employee_user_id = frappe.db.get_value("Employee", employee, "user_id")

	# --- 1. TICKET PERFORMANCE ---
	ticket_filters = {}
	if start_date:
		ticket_filters["creation"] = [">=", start_date + " 00:00:00"]
	if end_date:
		ticket_filters["creation"] = ["<=", end_date + " 23:59:59"]
		
	if employee_user_id:
		assigned_tickets = frappe.db.get_all("ToDo", {
			"reference_type": "Tactix Ticket",
			"allocated_to": employee_user_id
		}, pluck="reference_name") or [""]
		ticket_filters["name"] = ["in", assigned_tickets]
		
	tickets = frappe.get_list(
		"Tactix Ticket",
		filters=ticket_filters,
		fields=["first_response_time", "closed_time", "status"]
	)
	
	total_tickets = len(tickets)
	closed_resolved = sum(1 for t in tickets if t.status in ["Closed", "Resolved"])
	
	resp_times = [flt(t.first_response_time) for t in tickets if t.first_response_time is not None]
	avg_resp_time = sum(resp_times) / len(resp_times) if resp_times else 0.0
	
	close_times = [flt(t.closed_time) for t in tickets if t.closed_time is not None]
	avg_close_time = sum(close_times) / len(close_times) if close_times else 0.0
	
	ticket_resolution_rate = (closed_resolved / total_tickets * 100) if total_tickets > 0 else 0.0

	# --- 2. TASK PERFORMANCE ---
	task_filters = {}
	if start_date:
		task_filters["creation"] = [">=", start_date + " 00:00:00"]
	if end_date:
		task_filters["creation"] = ["<=", end_date + " 23:59:59"]
		
	if employee_user_id:
		assigned_tasks = frappe.db.get_all("Task Assigned To", {"user": employee_user_id}, pluck="parent") or [""]
		task_filters["name"] = ["in", assigned_tasks]
		
	tasks = frappe.get_list("Task", filters=task_filters, fields=["status", "is_overdue"])
	
	total_tasks = len(tasks)
	completed_tasks = sum(1 for t in tasks if t.status == "Completed")
	overdue_tasks = sum(1 for t in tasks if t.is_overdue)
	
	task_completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0

	# --- 3. TIMESHEET WORK HOURS ---
	timesheet_filters = {}
	if start_date:
		timesheet_filters["start_date"] = [">=", start_date]
	if end_date:
		timesheet_filters["end_date"] = ["<=", end_date]
	if employee:
		timesheet_filters["employee"] = employee
		
	timesheets = frappe.get_list(
		"Timesheet",
		filters=timesheet_filters,
		fields=["name", "total_hours", "start_date"]
	)
	
	total_hours = sum(flt(t.total_hours) for t in timesheets)
	active_days = len(set(t.start_date for t in timesheets if t.start_date))
	avg_daily_hours = (total_hours / active_days) if active_days > 0 else 0.0
	
	# Activity distribution breakdown
	activity_breakdown = {}
	ts_names = [t.name for t in timesheets]
	if ts_names:
		details = frappe.get_all(
			"Timesheet Detail",
			filters={"parent": ["in", ts_names]},
			fields=["activity_type", "hours"]
		)
		for d in details:
			act = d.activity_type or "Execution"
			activity_breakdown[act] = activity_breakdown.get(act, 0.0) + flt(d.hours)

	return {
		"ticket": {
			"total": total_tickets,
			"avg_response_time": avg_resp_time,
			"avg_close_time": avg_close_time,
			"resolution_rate": ticket_resolution_rate
		},
		"task": {
			"total": total_tasks,
			"completed": completed_tasks,
			"overdue": overdue_tasks,
			"completion_rate": task_completion_rate
		},
		"timesheet": {
			"total_hours": total_hours,
			"active_days": active_days,
			"avg_daily_hours": avg_daily_hours,
			"activities": activity_breakdown
		}
	}
