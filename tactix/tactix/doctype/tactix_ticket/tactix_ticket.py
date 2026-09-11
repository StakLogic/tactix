# Copyright (c) 2026, CodeVenturers and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TactixTicket(Document):
	def before_save(self):
		from frappe.utils import now_datetime, get_datetime

		# Record first response time
		if not self.is_new() and self.status != "Open" and not self.first_responded_on:
			self.first_responded_on = now_datetime()
			creation = self.creation or now_datetime()
			self.first_response_time = (get_datetime(self.first_responded_on) - get_datetime(creation)).total_seconds()

		# Record closed time
		if self.status == "Closed":
			# Verify if ticket raiser is allowed to close tickets
			from tactix.api.generic import get_tactix_settings
			settings = get_tactix_settings()
			if not settings.get("allow_ticket_raiser_to_close_tickets"):
				roles = frappe.get_roles(frappe.session.user)
				if "Tactix Ticket Raiser" in roles and "System Manager" not in roles and "Employee" not in roles:
					frappe.throw("Ticket closure is disabled for ticket raisers by system settings.")

			if not self.closed_on:
				self.closed_on = now_datetime()
				creation = self.creation or now_datetime()
				self.closed_time = (get_datetime(self.closed_on) - get_datetime(creation)).total_seconds()
		else:
			self.closed_on = None
			self.closed_time = 0

	def after_insert(self):
		from tactix.api.generic import create_notification_log

		# Fetch all users with "Support Team" role
		support_team_members = frappe.get_all("Has Role", filters={"role": "Support Team", "parenttype": "User"}, fields=["parent"])
		users = list(set([u.parent for u in support_team_members if frappe.db.exists("User", u.parent)]))

		
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
			create_notification_log(
				for_user=user,
				subject=f"New Ticket Raised: {self.subject}",
				document_type="Tactix Ticket",
				document_name=self.name,
				from_user=self.raised_by_user
			)

