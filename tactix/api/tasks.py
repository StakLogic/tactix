import frappe
import json
from frappe.utils import strip_html, now_datetime, time_diff_in_seconds, flt, today
from frappe.desk.form.assign_to import add
from frappe.model.db_query import DatabaseQuery


def count_doctype(doctype, filters=None, or_filters=None):
	res = DatabaseQuery(doctype).execute(filters=filters, or_filters=or_filters, fields=["count(*) as total_count"])
	return res[0].get("total_count") if res else 0


def _normalize_task_filters(filters):
	if isinstance(filters, str):
		filters = json.loads(filters)

	filters = dict(filters or {})

	if filters.get("assigned_to"):
		assigned_tasks = frappe.db.get_all("Task Assigned To", {"user": ["in", filters.get("assigned_to")]}, pluck="parent")
		filters["name"] = ["in", assigned_tasks]
		filters.pop("assigned_to")

	if filters.get("subject") and isinstance(filters["subject"], list) and len(filters["subject"]) == 2 and filters["subject"][0] == "like":
		query = filters["subject"][1]
		# Find tasks matching subject OR description using get_all (ignoring permissions here since main get_list applies permissions)
		matching_tasks = frappe.get_all("Task",
			filters=[],
			or_filters=[
				["subject", "like", query],
				["description", "like", query]
			],
			pluck="name"
		) or [""]

		if "name" in filters:
			existing_names = filters["name"][1]
			if not isinstance(existing_names, list):
				existing_names = [existing_names]
			intersected_names = list(set(existing_names) & set(matching_tasks)) or [""]
			filters["name"] = ["in", intersected_names]
		else:
			filters["name"] = ["in", matching_tasks]

		filters.pop("subject")

	if filters.get("status") and filters.get("status") == "Overdue":
		filters["is_overdue"] = True
		filters.pop("status")

	return filters


@frappe.whitelist()
def get_tasks(filters={}, start=0, page_length=20):
	filters = _normalize_task_filters(filters)

	user = frappe.session.user
	roles = frappe.get_roles(user)
	or_filters = None
	if "Employee" in roles and "System Manager" not in roles:
		assigned_tasks = frappe.db.get_all("Task Assigned To", {"user": user}, pluck="parent") or [""]
		or_filters = [
			["name", "in", assigned_tasks],
			["owner", "=", user],
			["assigned_by", "=", user]
		]

	# Get total count matching current filters (before pagination slice)
	total_count = count_doctype("Task", filters=filters or {}, or_filters=or_filters)

	start = int(start)
	page_length = int(page_length)

	# Use get_list for the main task list
	tasks = frappe.get_list(
		"Task",
		fields=[
			"name", "subject", "project", "priority", "expected_time", "owner", "is_overdue", "department",
			"status", "exp_end_date", "assigned_by", "description", "assigned_datetime", "completed_by", "fullfilled_in_display_text",
			"tactix_team"
		],
		filters=filters or {},
		or_filters=or_filters,
		order_by="modified desc",
		limit_start=start,
		limit_page_length=page_length
	)

	for row in tasks:
		assigned_users = frappe.get_all("Task Assigned To", 
			filters={"parent": row.name}, 
			pluck="user"
		)

		row["description_for_list"] = strip_html(row.description or "")
		row["assigned_to"] = assigned_users
		if row.project:
			row["project_name"] = frappe.db.get_value("Project", row.project, "project_name")

		attachments = frappe.db.get_all("File", {"attached_to_doctype": "Task", "attached_to_name": row.name}, ["file_name", "file_url"])
		row["attachments"] = attachments

		row["has_unseen_comments"] = 0
		if has_unseen_comments := frappe.db.count(
				"Comment", 
				{"comment_type": "Comment", "reference_doctype": "Task", "reference_name": row.name, "seen": 0}
			):
			row["has_unseen_comments"] = has_unseen_comments

	return {
		"tasks": tasks,
		"total_count": total_count
	}


@frappe.whitelist()
def get_task_summary(filters={}):
	filters = _normalize_task_filters(filters)

	base_filters = dict(filters)
	open_filters = dict(base_filters, status="Open")
	in_progress_working_filters = dict(base_filters, status="Working")
	in_progress_review_filters = dict(base_filters, status="Pending Review")
	completed_filters = dict(base_filters, status="Completed")
	overdue_filters = dict(base_filters, is_overdue=True)
	
	user = frappe.session.user
	roles = frappe.get_roles(user)
	or_filters = None
	if "Employee" in roles and "System Manager" not in roles:
		assigned_tasks = frappe.db.get_all("Task Assigned To", {"user": user}, pluck="parent") or [""]
		or_filters = [
			["name", "in", assigned_tasks],
			["owner", "=", user],
			["assigned_by", "=", user]
		]

	project_rows = frappe.get_list(
		"Task",
		fields=["project"],
		filters=base_filters,
		or_filters=or_filters,
	)
	active_projects_count = len({row.project for row in project_rows if row.project})

	return {
		"total": count_doctype("Task", filters=base_filters, or_filters=or_filters),
		"open": count_doctype("Task", filters=open_filters, or_filters=or_filters),
		"working": count_doctype("Task", filters=in_progress_working_filters, or_filters=or_filters),
		"pending_review": count_doctype("Task", filters=in_progress_review_filters, or_filters=or_filters),
		"in_progress": count_doctype("Task", filters=in_progress_working_filters, or_filters=or_filters) + count_doctype("Task", filters=in_progress_review_filters, or_filters=or_filters),
		"completed": count_doctype("Task", filters=completed_filters, or_filters=or_filters),
		"overdue": count_doctype("Task", filters=overdue_filters, or_filters=or_filters),
		"active_projects": active_projects_count,
	}


@frappe.whitelist()
def update_task_status(name, status):
	task = frappe.get_doc("Task", name)
	task.status = status
	task.save()
	return task.name


@frappe.whitelist()
def create_task(doc):
	if isinstance(doc, str):
		doc = json.loads(doc)
	try:
		new_task = frappe.get_doc({
			"doctype": "Task",
			"subject": doc.get("subject"),
			"project": doc.get("project"),
			"status": doc.get("status"),
			"priority": doc.get("priority"),
			"exp_end_date": doc.get("exp_end_date"),
			"description": doc.get("description"),
			"assigned_by": doc.get("assigned_by"),
			"expected_time": doc.get("expected_time"),
			"department": doc.get("department"),
			"tactix_ticket": doc.get("ticket"),
			"tactix_team": doc.get("tactix_team") or doc.get("team"),
			# Custom logic for assigned_to if it's a link or user field
			# "assigned_to": doc.get("assigned_to"),
		})

		if doc.get("assigned_to"):
			for user in doc.get("assigned_to"):
				new_task.append("assigned_to_users", {"user": user})

			new_task.assigned_datetime = now_datetime()
		
		new_task.insert()
		assign_tasks(task=new_task, assigned_users=doc.get("assigned_to"), removed_users=[])

		for file in doc.get("attachments") or []:
			file_name = frappe.db.get_value("File", {"file_url": file.get("file_url")}, "name")
			if file_name:
				frappe.db.set_value("File", file_name, {"attached_to_doctype": "Task", "attached_to_name": new_task.name})

		if description := doc.get("description"):
			import re
			file_urls = re.findall(r'src=["\']([^"\']+)["\']', description)
			for url in file_urls:
				file_name = frappe.db.get_value("File", {"file_url": url}, "name")
				if file_name:
					frappe.db.set_value("File", file_name, {"attached_to_doctype": "Task", "attached_to_name": new_task.name})

		for row in new_task.assigned_to_users:
			publish_assignment_notification(
				user=row.user,
				docname=new_task.name,
				action="assigned",
				subject=new_task.get("subject"),
				assigned_by=new_task.get("assigned_by"),
			)
		
		return new_task.name
	except Exception as e:
		frappe.log_error(title="Error creating task: from Ticket", message=str(e))
		return {"error": str(e)}


@frappe.whitelist()
def edit_task(name, doc):
	if isinstance(doc, str):
		doc = json.loads(doc)

	task = frappe.get_doc("Task", name)

	# testig socket io
	frappe.publish_realtime(
		"test_socket_io", 
		{"docname": task.name, "title": "test", "subject": "test"},
		after_commit=True
	)

	# Update fields
	task.update({
		"subject": doc.get("subject"),
		"project": doc.get("project"),
		"status": doc.get("status"),
		"priority": doc.get("priority"),
		"exp_end_date": doc.get("exp_end_date"),
		"description": doc.get("description"),
		"assigned_by": doc.get("assigned_by"),
		"expected_time": doc.get("expected_time"),
		"department": doc.get("department"),
		"tactix_team": doc.get("tactix_team") or doc.get("team"),
	})

	# Current users in Task
	existing_users = [row.user for row in task.get("assigned_to_users")]

	# New users coming from doc
	assigned_users = doc.get("assigned_to") or []

	# --- Remove users that no longer exist ---
	removed_users = []
	for row in task.get("assigned_to_users")[:]:
		if row.user not in assigned_users:
			task.remove(row)
			removed_users.append(row.user)

	# --- Add new users ---
	assigned_new_users = []
	for user in assigned_users:
		if user and user not in existing_users:
			task.append("assigned_to_users", {
				"user": user
			})
			publish_assignment_notification(
				user=user,
				docname=task.name,
				action="assigned",
				subject=doc.get("subject"),
				assigned_by=doc.get("assigned_by"),
			)
			assigned_new_users.append(user)

	for user in removed_users:
		publish_assignment_notification(
			user=user,
			docname=task.name,
			action="removed",
			subject=doc.get("subject") or task.get("subject"),
			assigned_by=doc.get("assigned_by") or task.get("assigned_by"),
		)

	incoming_files = doc.get("attachments") or []
	incoming_file_urls = {f.get("file_url") for f in incoming_files if f.get("file_url")}

	if description := doc.get("description"):
		import re
		desc_file_urls = re.findall(r'src=["\']([^"\']+)["\']', description)
		for url in desc_file_urls:
			incoming_file_urls.add(url)

	existing_files = frappe.get_all(
		"File",
		filters={
			"attached_to_doctype": "Task",
			"attached_to_name": task.name
		},
		fields=["name", "file_url"]
	)

	existing_file_urls = {f.file_url for f in existing_files}

	files_to_remove = existing_file_urls - incoming_file_urls

	for file in existing_files:
		if file.file_url in files_to_remove:
			frappe.db.set_value("File", file.name, {
				"attached_to_doctype": None,
				"attached_to_name": None
			})

	files_to_add = incoming_file_urls - existing_file_urls

	for file_url in files_to_add:
		file_name = frappe.db.get_value("File", {"file_url": file_url}, "name")
		if file_name:
			frappe.db.set_value("File", file_name, {
				"attached_to_doctype": "Task",
				"attached_to_name": task.name
			})

	task.save()

	assign_tasks(task=task, assigned_users=assigned_new_users, removed_users=removed_users)

	return task.name


@frappe.whitelist()
def get_comments(task):
	comments = frappe.get_all(
		"Comment",
		fields=[
			"comment_email", "name", "comment_by", "subject", "content", "creation"
		],
		filters={"comment_type": "Comment", "reference_doctype": "Task", "reference_name": task},
		order_by="creation asc"
	)

	return comments


@frappe.whitelist()
def add_comment(task, content):
	"""Adds a new comment to a specific Task"""
	if not content:
		frappe.throw("Comment content cannot be empty")
		
	doc = frappe.get_doc({
		"doctype": "Comment",
		"comment_type": "Comment",
		"reference_doctype": "Task",
		"reference_name": task,
		"content": content,
		"comment_by": frappe.session.user
	})
	doc.insert(ignore_permissions=True)
	return doc


@frappe.whitelist()
def edit_comment(name, content):
	"""Edits an existing comment by its unique name ID"""
	doc = frappe.get_doc("Comment", name)
	
	# Optional: Check if the current user is the author
	if doc.comment_email != frappe.session.user and frappe.session.user != "Administrator":
		frappe.throw("You are not allowed to edit this comment", frappe.PermissionError)
		
	doc.content = content
	doc.save(ignore_permissions=True)
	return doc


@frappe.whitelist()
def delete_comment(name):
	"""Deletes a comment by its name ID"""
	doc = frappe.get_doc("Comment", name)
	
	# Optional: Permission check
	if doc.comment_email != frappe.session.user and frappe.session.user != "Administrator":
		frappe.throw("You are not allowed to delete this comment", frappe.PermissionError)
		
	frappe.delete_doc("Comment", name)
	return "Success"


def publish_assignment_notification(user, docname, action, subject, assigned_by=None):
	frappe.publish_realtime(
		"tactix_task_assignment",
		{
			"docname": docname,
			"action": action,
			"title": "Task Assigned" if action == "assigned" else "Task Removed",
			"subject": str(subject or ""),
			"assigned_by": str(assigned_by or ""),
		},
		user=user,
		after_commit=True,
	)


def assign_tasks(task, assigned_users, removed_users):
	args = {
		"assign_to": assigned_users,
		"doctype": "Task",
		"name": task.name,
		"description": task.description or task.subject,
	}
	add(args)

	if task.tactix_ticket:
		ticket_args = {
			"assign_to": assigned_users,
			"doctype": "Tactix Ticket",
			"name": task.tactix_ticket,
			"description": task.subject,
		}
		add(ticket_args)

	if removed_users:
		for user in removed_users:
			frappe.db.delete("ToDo", {"reference_type": "Task", "reference_name": task.name, "allocated_to": user})
			if task.tactix_ticket:
				frappe.db.delete("ToDo", {"reference_type": "Tactix Ticket", "reference_name": task.tactix_ticket, "allocated_to": user})