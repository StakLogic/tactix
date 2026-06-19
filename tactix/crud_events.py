import frappe
import json
from frappe.utils import strip_html, now_datetime, time_diff_in_seconds, flt, today, now, getdate

def update_task(doc, method=None):
	if doc.assigned_to_users and not doc.assigned_datetime:
		doc.assigned_datetime = now_datetime()

	if doc.status in ["Completed", "Pending Review"] and not doc.completed_on:
		doc.completed_datetime = now_datetime()
		doc.completed_on = today()
		doc.completed_by = frappe.session.user
		total_seconds = time_diff_in_seconds(doc.completed_datetime, doc.assigned_datetime)
		doc.fullfilled_in = total_seconds / 60

		minutes = total_seconds / 60
		hours = total_seconds / 3600
		days = total_seconds / 86400

		doc.fullfilled_in_display_text = f"{flt(days,2)} Days {flt(hours,2)} Hrs {flt(minutes,2)} Min"

	if doc.exp_end_date and (getdate(doc.exp_end_date) < getdate(today())):
		doc.is_overdue = 1
	else:
		doc.is_overdue = 0


def set_tasks_as_overdue():
	frappe.db.set_value(
		"Task",
		{"exp_end_date": ["<", getdate(today())], "is_overdue": 0, "completed_datetime": ["is", "not set"]},
		"is_overdue",
		1
	)