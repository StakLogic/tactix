import frappe
from frappe import _
import json
from frappe.model.db_query import DatabaseQuery


def count_doctype(doctype, filters=None, or_filters=None):
	res = DatabaseQuery(doctype).execute(filters=filters, or_filters=or_filters, fields=["count(*) as total_count"])
	return res[0].get("total_count") if res else 0


def _normalize_ticket_filters(filters):
	if isinstance(filters, str):
		filters = json.loads(filters)

	return dict(filters or {})

@frappe.whitelist()
def get_tickets(filters=None, start=0, page_length=20):
	"""Fetch tickets based on filters and search query."""
	filters = _normalize_ticket_filters(filters)

	user = frappe.session.user
	roles = frappe.get_roles(user)
	or_filters = None
	if "System Manager" not in roles and "Support Team" not in roles:
		user_details = frappe.db.get_value("User", user, ["tactix_customer", "tactix_department"], as_dict=True) or {}
		customer = user_details.get("tactix_customer")
		department = user_details.get("tactix_department")

		if "Tactix Ticket Raiser" in roles:
			if customer:
				filters["customer"] = customer
			if department:
				filters["department"] = department

		or_filters = []
		if "Employee" in roles:
			assigned_tickets = frappe.db.get_all("ToDo", {
				"reference_type": "Tactix Ticket",
				"allocated_to": user,
				"status": "Open"
			}, pluck="reference_name") or [""]
			or_filters.append(["name", "in", assigned_tickets])
			or_filters.append(["owner", "=", user])
			or_filters.append(["raised_by_user", "=", user])

		if "Tactix Ticket Raiser" in roles:
			is_dept_head = False
			if department:
				is_dept_head = bool(frappe.db.exists("Tactix Department", {"name": department, "department_head": user}))
			
			if is_dept_head and department:
				or_filters.append(["department", "=", department])
			or_filters.append(["owner", "=", user])
			or_filters.append(["raised_by_user", "=", user])

		if not or_filters:
			or_filters.append(["owner", "=", user])
			or_filters.append(["raised_by_user", "=", user])
	
	# Get total count matching current filters (before pagination slice)
	total_count = count_doctype("Tactix Ticket", filters=filters or {}, or_filters=or_filters)

	start = int(start)
	page_length = int(page_length)

	tickets = frappe.get_list(
		"Tactix Ticket",
		filters=filters or {},
		or_filters=or_filters,
		fields=[
			"name", "subject", "raised_by", "status", "department",
			"priority", "ticket_type", "opening_date", "description",
			"customer", "agent_group", "resolution_details", "creation",
			"first_response_time", "first_responded_on", "closed_on", "closed_time",
		],
		order_by="creation desc",
		limit_start=start,
		limit_page_length=page_length
	)

	for row in tickets:
		row["attachments"] = []
		attachments = frappe.db.get_all("Tactix Ticket Attachment", {"parent": row.name}, pluck="attach")
		if attachments:
			files = frappe.db.get_all(
				"File",
				filters={"file_url": ["in", attachments]},
				fields=["file_url", "file_name"]
			)
			row["attachments"] = files

	return {
		"tickets": tickets,
		"total_count": total_count
	}


@frappe.whitelist()
def get_ticket_summary(filters=None):
	filters = _normalize_ticket_filters(filters)

	user = frappe.session.user
	roles = frappe.get_roles(user)
	or_filters = None
	if "System Manager" not in roles:
		user_details = frappe.db.get_value("User", user, ["tactix_customer", "tactix_department"], as_dict=True) or {}
		customer = user_details.get("tactix_customer")
		department = user_details.get("tactix_department")

		if "Tactix Ticket Raiser" in roles:
			if customer:
				filters["customer"] = customer
			if department:
				filters["department"] = department

		or_filters = []
		if "Employee" in roles:
			assigned_tickets = frappe.db.get_all("ToDo", {
				"reference_type": "Tactix Ticket",
				"allocated_to": user,
				"status": "Open"
			}, pluck="reference_name") or [""]
			or_filters.append(["name", "in", assigned_tickets])
			or_filters.append(["owner", "=", user])
			or_filters.append(["raised_by_user", "=", user])

		if "Tactix Ticket Raiser" in roles:
			is_dept_head = False
			if department:
				is_dept_head = bool(frappe.db.exists("Tactix Department", {"name": department, "department_head": user}))
			
			if is_dept_head and department:
				or_filters.append(["department", "=", department])
			or_filters.append(["owner", "=", user])
			or_filters.append(["raised_by_user", "=", user])

		if not or_filters:
			or_filters.append(["owner", "=", user])
			or_filters.append(["raised_by_user", "=", user])

	base_filters = dict(filters)
	open_filters = dict(base_filters, status="Open")
	replied_filters = dict(base_filters, status="Replied")
	resolved_filters = dict(base_filters, status="Resolved")
	closed_filters = dict(base_filters, status="Closed")
	urgent_filters = dict(base_filters, priority="Urgent")

	return {
		"total": count_doctype("Tactix Ticket", filters=base_filters, or_filters=or_filters),
		"open": count_doctype("Tactix Ticket", filters=open_filters, or_filters=or_filters),
		"replied": count_doctype("Tactix Ticket", filters=replied_filters, or_filters=or_filters),
		"resolved": count_doctype("Tactix Ticket", filters=resolved_filters, or_filters=or_filters),
		"closed": count_doctype("Tactix Ticket", filters=closed_filters, or_filters=or_filters),
		"urgent": count_doctype("Tactix Ticket", filters=urgent_filters, or_filters=or_filters),
	}

@frappe.whitelist()
def create_ticket(doc):
	"""Create a new Ticket document."""
	if isinstance(doc, str):
		doc = json.loads(doc)
	
	attachments = doc.pop("attachments", [])
	
	new_doc = frappe.get_doc({
		"doctype": "Tactix Ticket",
		**doc
	})
	
	for file in attachments:
		file_url = file.get("file_url")
		if file_url:
			new_doc.append("attachments", {"attach": file_url})
			
	new_doc.insert()
	return new_doc.name


@frappe.whitelist()
def edit_ticket(name, doc):
	"""Update an existing Ticket document."""
	if isinstance(doc, str):
		doc = json.loads(doc)

	ticket = frappe.get_doc("Tactix Ticket", name)

	# Extract incoming attachments safely
	incoming_files = doc.pop("attachments", [])
	incoming_file_urls = {
		f.get("file_url") for f in incoming_files if f.get("file_url")
	}

	# Existing child table attachments
	existing_file_urls = {
		d.attach for d in ticket.attachments if d.attach
	}

	files_to_remove = existing_file_urls - incoming_file_urls
	files_to_add = incoming_file_urls - existing_file_urls

	ticket.attachments = [
		d for d in ticket.attachments if d.attach not in files_to_remove
	]

	for file_url in files_to_add:
		ticket.append("attachments", {"attach": file_url})

	# Update other fields
	ticket.update(doc)
	ticket.save(ignore_permissions=True)

	return ticket.name


@frappe.whitelist()
def get_agent_group_options():
	"""Fetch Agent Groups for the filter/form dropdown."""
	groups = [{"customer_name": "Test", "name": "Test"}]
	return [{"label": c.get("customer_name"), "value": c.get("name"),} for c in groups]

@frappe.whitelist()
def get_comments(ticket):
	"""Retrieve all comments linked to a specific ticket."""
	return frappe.get_all(
		"Comment",
		filters={
			"comment_type": "Comment",
			"reference_doctype": "Tactix Ticket",
			"reference_name": ticket
		},
		fields=["name", "content", "owner", "comment_by", "creation"],
		order_by="creation asc"
	)

@frappe.whitelist()
def edit_comment(name, content):
	"""Edits an existing comment by its unique name ID"""
	doc = frappe.get_doc("Comment", name)
	
	if doc.owner != frappe.session.user and doc.comment_email != frappe.session.user and frappe.session.user != "Administrator":
		frappe.throw("You are not allowed to edit this comment", frappe.PermissionError)
		
	doc.content = content
	doc.save(ignore_permissions=True)
	return doc


@frappe.whitelist()
def delete_comment(name):
	"""Deletes a comment by its name ID"""
	doc = frappe.get_doc("Comment", name)
	
	if doc.owner != frappe.session.user and doc.comment_email != frappe.session.user and frappe.session.user != "Administrator":
		frappe.throw("You are not allowed to delete this comment", frappe.PermissionError)
		
	frappe.delete_doc("Comment", name)
	return "Success"


@frappe.whitelist()
def add_comment(ticket, content):
	"""Add a new comment to a ticket's timeline."""
	doc = frappe.get_doc("Tactix Ticket", ticket)
	comment = doc.add_comment("Comment", text=content)
	return comment.name


@frappe.whitelist()
def create_tactix_ticket():
	try:
		data = frappe.request.json

		doc = data.get("doc")
		attachments = data.get("attachments", [])

		new_doc = frappe.get_doc({
			"doctype": "Tactix Ticket",
			**doc
		})	

		new_doc.insert(ignore_permissions=True)
		for file in attachments:
			new_doc.append("attachments", {"attach": file.get("file_url")})
			frappe.db.set_value("File", file.get("name"), {"attached_to_doctype": "Tactix Ticket", "attached_to_name": new_doc.name})

		new_doc.save()
		return new_doc.name
	except Exception as e:
		frappe.log_error(message=str(frappe.get_traceback()), title="Error creating Tactix Ticket")
		return {"error": str(e)}


@frappe.whitelist()
def check_portal_user(email):
	"""Check if portal user exists"""

	if frappe.db.exists("User", email):
		return {
			"exists": True
		}

	return {
		"exists": False
	}

@frappe.whitelist()
def create_portal_user():
	"""Create portal user for ticket raising"""
	try:
		data = frappe.request.json

		if frappe.db.exists("User", data.get("email")):
			return {
				"exists": True,
				"user": data.get("email")
			}

		department = {}
		if data.get("department") and not frappe.db.exists("Tactix Department", data.get("department")):
			department = frappe.get_doc({
				"doctype": "Tactix Department",
				"department_name": data.get("department"),
			})
			department.insert(ignore_permissions=True)


		user = frappe.get_doc({
			"doctype": "User",
			"email": data.get("email"),
			"first_name": data.get("first_name"),
			"enabled": 1,
			"tactix_customer": data.get("customer"),
			"tactix_department": data.get("department"),
			"roles": [
				{"role": "Tactix Ticket Raiser"}
			],
			"modules": [],
		})

		user.insert(ignore_permissions=True)

		if department and data.get("is_department_head"):
			department.department_head = user.name
			department.save()

		return {
			"exists": False,
			"user": user.name,
		}
	except Exception as e:
		frappe.log_error(message=str(frappe.get_traceback()), title="Error creating Tactix Portal User")
		return {"error": str(e)}