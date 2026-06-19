import frappe
from erpnext.projects.doctype.task.task import Task


class CustomTask(Task):
	def update_status(self):
		return