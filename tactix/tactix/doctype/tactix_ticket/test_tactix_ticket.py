import frappe
from frappe.tests.utils import FrappeTestCase

class TestTactixTicket(FrappeTestCase):
	def test_response_and_closed_times(self):
		# 1. Create a ticket (defaults to Open)
		doc = frappe.get_doc({
			"doctype": "Tactix Ticket",
			"subject": "Test Automated Ticket",
			"status": "Open",
			"priority": "Medium",
			"description": "Test description"
		})
		doc.insert()
		
		self.assertIsNone(doc.first_responded_on)
		self.assertTrue(doc.first_response_time is None or doc.first_response_time == 0)
		self.assertIsNone(doc.closed_on)
		self.assertTrue(doc.closed_time is None or doc.closed_time == 0)

		# 2. Change status to Replied
		doc.status = "Replied"
		doc.save()
		
		self.assertIsNotNone(doc.first_responded_on)
		self.assertGreaterEqual(doc.first_response_time, 0)
		self.assertIsNone(doc.closed_on)
		self.assertEqual(doc.closed_time, 0)

		# Store first response time to check it is not overwritten later
		first_resp = doc.first_responded_on
		first_resp_time = doc.first_response_time

		# 3. Change status to Closed
		doc.status = "Closed"
		doc.save()
		
		self.assertEqual(doc.first_responded_on, first_resp)
		self.assertEqual(doc.first_response_time, first_resp_time)
		self.assertIsNotNone(doc.closed_on)
		self.assertGreaterEqual(doc.closed_time, 0)

		# 4. Reopen/change status back to Replied
		doc.status = "Replied"
		doc.save()
		
		self.assertEqual(doc.first_responded_on, first_resp)
		self.assertEqual(doc.first_response_time, first_resp_time)
		self.assertIsNone(doc.closed_on)
		self.assertEqual(doc.closed_time, 0)

		# Clean up
		doc.delete()
