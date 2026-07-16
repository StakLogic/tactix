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

def get_employee_github_username(employee):
	if not employee:
		return None
	github_username = None
	try:
		github_username = frappe.db.get_value("Employee", employee, "github_username")
	except Exception:
		pass
		
	if github_username:
		return github_username
		
	# Fallback fuzzy mapping
	emp_details = frappe.db.get_value("Employee", employee, ["employee_name", "user_id"], as_dict=True)
	if emp_details:
		name = emp_details.get("employee_name")
		email = emp_details.get("user_id")
		
		# Try email prefix
		if email:
			email_prefix = email.split("@")[0].lower()
			if frappe.db.exists("Tactix Pull Request", {"author_login": ["like", f"%{email_prefix}%"]}):
				matched = frappe.db.get_value("Tactix Pull Request", {"author_login": ["like", f"%{email_prefix}%"]}, "author_login")
				if matched:
					return matched
					
		# Try slugified employee name
		if name:
			slug = name.lower().replace(" ", "-")
			if frappe.db.exists("Tactix Pull Request", {"author_login": ["like", f"%{slug}%"]}):
				matched = frappe.db.get_value("Tactix Pull Request", {"author_login": ["like", f"%{slug}%"]}, "author_login")
				if matched:
					return matched
					
			slug_no_dash = name.lower().replace(" ", "")
			if frappe.db.exists("Tactix Pull Request", {"author_login": ["like", f"%{slug_no_dash}%"]}):
				matched = frappe.db.get_value("Tactix Pull Request", {"author_login": ["like", f"%{slug_no_dash}%"]}, "author_login")
				if matched:
					return matched
					
	return None

def _get_timeline_data(timespan, start_date, end_date, prs, tasks, tickets, timesheets):
	import datetime
	
	labels = []
	pr_series = []
	task_series = []
	ticket_series = []
	hour_series = []
	
	# Determine start and end date objects
	today_dt = getdate(today())
	if not start_date:
		start_dt = add_days(today_dt, -180)
		end_dt = today_dt
		grouping = "month"
	else:
		start_dt = getdate(start_date)
		end_dt = getdate(end_date)
		delta = (end_dt - start_dt).days
		if delta <= 1:
			grouping = "hour"
		elif delta <= 14:
			grouping = "day"
		elif delta <= 60:
			grouping = "day"
		else:
			grouping = "month"
			
	# Initialize buckets
	buckets = {}
	if grouping == "hour":
		for h in range(24):
			buckets[f"{h:02d}:00"] = {"prs": 0, "tasks": 0, "tickets": 0, "hours": 0.0}
			labels.append(f"{h:02d}:00")
	elif grouping == "day":
		curr = start_dt
		while curr <= end_dt:
			date_str = curr.strftime("%Y-%m-%d")
			label_str = curr.strftime("%b %d")
			buckets[date_str] = {"prs": 0, "tasks": 0, "tickets": 0, "hours": 0.0}
			labels.append(label_str)
			curr += datetime.timedelta(days=1)
	elif grouping == "month":
		curr = start_dt.replace(day=1)
		while curr <= end_dt:
			month_str = curr.strftime("%Y-%m")
			label_str = curr.strftime("%b %Y")
			buckets[month_str] = {"prs": 0, "tasks": 0, "tickets": 0, "hours": 0.0}
			labels.append(label_str)
			if curr.month == 12:
				curr = curr.replace(year=curr.year + 1, month=1)
			else:
				curr = curr.replace(month=curr.month + 1)

	# Helper to get bucket key
	def get_key(dt_val):
		if not dt_val or isinstance(dt_val, (int, float)):
			return None
		if isinstance(dt_val, str):
			if "T" in dt_val:
				dt_val = dt_val.split("T")[0]
			elif " " in dt_val:
				dt_val = dt_val.split(" ")[0]
			dt_val = getdate(dt_val)
		elif isinstance(dt_val, datetime.datetime):
			dt_val = dt_val.date()
			
		if grouping == "hour":
			if isinstance(dt_val, datetime.date) and not isinstance(dt_val, datetime.datetime):
				return "12:00"
			return f"{dt_val.hour:02d}:00"
		elif grouping == "day":
			return dt_val.strftime("%Y-%m-%d")
		elif grouping == "month":
			return dt_val.strftime("%Y-%m")
		return None

	for pr in prs:
		k = get_key(pr.get("github_created_at"))
		if k in buckets:
			buckets[k]["prs"] += 1
			
	for task in tasks:
		dt = task.get("completed_datetime") or task.get("creation")
		k = get_key(dt)
		if k in buckets:
			buckets[k]["tasks"] += 1
			
	for ticket in tickets:
		dt = ticket.get("creation")
		k = get_key(dt)
		if k in buckets:
			buckets[k]["tickets"] += 1
			
	for ts in timesheets:
		k = get_key(ts.get("start_date"))
		if k in buckets:
			buckets[k]["hours"] += flt(ts.get("total_hours"))

	# Flatten to lists matching labels order
	if grouping == "hour":
		for h in range(24):
			key = f"{h:02d}:00"
			b = buckets[key]
			pr_series.append(b["prs"])
			task_series.append(b["tasks"])
			ticket_series.append(b["tickets"])
			hour_series.append(b["hours"])
	elif grouping == "day":
		curr = start_dt
		while curr <= end_dt:
			key = curr.strftime("%Y-%m-%d")
			b = buckets[key]
			pr_series.append(b["prs"])
			task_series.append(b["tasks"])
			ticket_series.append(b["tickets"])
			hour_series.append(b["hours"])
			curr += datetime.timedelta(days=1)
	elif grouping == "month":
		curr = start_dt.replace(day=1)
		while curr <= end_dt:
			key = curr.strftime("%Y-%m")
			b = buckets[key]
			pr_series.append(b["prs"])
			task_series.append(b["tasks"])
			ticket_series.append(b["tickets"])
			hour_series.append(b["hours"])
			if curr.month == 12:
				curr = curr.replace(year=curr.year + 1, month=1)
			else:
				curr = curr.replace(month=curr.month + 1)

	return {
		"labels": labels,
		"prs": pr_series,
		"tasks": task_series,
		"tickets": ticket_series,
		"hours": hour_series
	}

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
		fields=["first_response_time", "closed_time", "status", "creation"]
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
		
	tasks = frappe.get_list("Task", filters=task_filters, fields=["status", "is_overdue", "completed_datetime", "creation"])
	
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

	# --- 4. GITHUB PERFORMANCE ---
	pr_filters = {}
	if start_date:
		pr_filters["github_created_at"] = [">=", start_date]
	if end_date:
		pr_filters["github_created_at"] = ["<=", f"{end_date}T23:59:59Z"]
		
	github_username = None
	if employee:
		github_username = get_employee_github_username(employee)
		if github_username:
			pr_filters["author_login"] = github_username
		else:
			pr_filters["author_login"] = "___non_existent_user___"
			
	prs = frappe.get_all(
		"Tactix Pull Request",
		filters=pr_filters,
		fields=["github_id", "title", "state", "is_merged", "github_created_at", "comments_count", "repository_url"]
	)
	
	total_prs = len(prs)
	merged_prs = sum(1 for p in prs if p.is_merged)
	open_prs = sum(1 for p in prs if p.state == "open")
	closed_prs = sum(1 for p in prs if p.state == "closed" and not p.is_merged)
	comments_count = sum(p.comments_count or 0 for p in prs)
	repos_count = len(set(p.repository_url for p in prs if p.repository_url))
	
	merged_rate = (merged_prs / total_prs * 100) if total_prs > 0 else 0.0

	timeline_data = _get_timeline_data(timespan, start_date, end_date, prs, tasks, tickets, timesheets)

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
		},
		"github": {
			"total_prs": total_prs,
			"merged_prs": merged_prs,
			"open_prs": open_prs,
			"closed_prs": closed_prs,
			"merged_rate": merged_rate,
			"comments_count": comments_count,
			"repos_count": repos_count,
			"username": github_username
		},
		"timeline": timeline_data
	}
