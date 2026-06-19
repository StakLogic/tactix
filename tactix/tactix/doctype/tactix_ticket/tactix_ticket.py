# Copyright (c) 2026, CodeVenturers and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TactixTicket(Document):
	def after_insert(self):
		# Fetch all users with "Support Team" role
		support_team_members = frappe.get_all("Has Role", filters={"role": "Support Team"}, fields=["parent"])
		users = list(set([u.parent for u in support_team_members]))
		
		# Publish a real-time event to each connected Support Team member
		for user in users:
			frappe.publish_realtime(
				event="tactix_ticket_raised",
				message={
					"name": self.name,
					"subject": self.subject,
					"raised_by": self.raised_by or self.owner,
					"priority": self.priority,
					"creation": str(self.creation),
				},
				user=user,
				after_commit=True
			)

