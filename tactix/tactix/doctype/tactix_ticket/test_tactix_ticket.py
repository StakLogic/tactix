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

	def test_timesheet_api(self):
		from tactix.api.timesheet import create_timesheet, get_timesheets, get_timesheet_summary
		
		frappe.set_user("Administrator")
		employee = get_employee_stub()
		
		task = frappe.get_doc({
			"doctype": "Task",
			"subject": "Test Timesheet Task",
			"status": "Open"
		}).insert()
		
		import random
		test_date = frappe.utils.add_to_date(frappe.utils.today(), days=random.randint(100, 10000))

		doc_payload = {
			"date": test_date,
			"employee": employee,
			"time_logs": [
				{
					"task": task.name,
					"hours": 4.5,
					"activity_type": "Planning",
					"description": "Planning unit tests"
				}
			],
			"submit": 0
		}
		
		ts_name = create_timesheet(doc_payload)
		self.assertIsNotNone(ts_name)
		
		ts = frappe.get_doc("Timesheet", ts_name)
		self.assertEqual(ts.employee, employee)
		self.assertEqual(ts.total_hours, 4.5)
		self.assertEqual(ts.status, "Draft")
		self.assertEqual(len(ts.time_logs), 1)
		self.assertEqual(ts.time_logs[0].task, task.name)
		self.assertEqual(ts.time_logs[0].hours, 4.5)
		
		res_list = get_timesheets(filters={"name": ts_name})
		self.assertEqual(res_list.get("total_count"), 1)
		
		res_summary = get_timesheet_summary(filters={"name": ts_name})
		self.assertEqual(res_summary.get("total_hours"), 4.5)
		self.assertEqual(res_summary.get("draft_count"), 1)
		
		ts.delete()
		task.delete()

	def test_performance_api(self):
		from tactix.api.performance import get_performance_data
		
		frappe.set_user("Administrator")
		employee = get_employee_stub()
		
		data = get_performance_data(employee=employee, timespan="this_month")
		self.assertIsNotNone(data)
		self.assertIn("ticket", data)
		self.assertIn("task", data)
		self.assertIn("timesheet", data)

def get_employee_stub():
	employee = frappe.db.get_value("Employee", {"user_id": "Administrator"})
	if not employee:
		employee = frappe.db.get_value("Employee", {})
	if not employee:
		emp_doc = frappe.get_doc({
			"doctype": "Employee",
			"employee_name": "Administrator",
			"user_id": "Administrator",
			"company": frappe.db.get_single_value("Global Defaults", "default_company") or "Test Company",
			"status": "Active"
		})
		emp_doc.insert(ignore_permissions=True)
		employee = emp_doc.name
	return employee
