# Copyright (c) 2026, Jay Anjarlekar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class ChangeRecord(Document):
	def before_insert(self):
		self.set_defaults()
		if not self.workflow_state:
			self.workflow_state = "Draft"
		if not self.status:
			self.status = "Draft"

	def before_save(self):
		self.log_workflow_transition()

	def validate(self):
		self.set_workgroup_owner_details()
		self.validate_timelines()

	def set_defaults(self):
		if not self.requestor:
			self.requestor = frappe.session.user

		if not self.logged_time:
			self.logged_time = now_datetime()

		if self.owner_workgroup and not self.assigned_workgroup:
			self.assigned_workgroup = self.owner_workgroup

	def set_workgroup_owner_details(self):
		if not self.owner_workgroup:
			self.workgroup_owner_details = ""
			return

		self.workgroup_owner_details = get_workgroup_owner_details(self.owner_workgroup)

	def validate_timelines(self):
		if self.planned_start_time and self.planned_end_time:
			if self.planned_end_time <= self.planned_start_time:
				frappe.throw("Planned End Time must be after Planned Start Time")

		if self.is_downtime_required == "Yes":
			if self.downtime_start and self.downtime_end and self.downtime_end <= self.downtime_start:
				frappe.throw("Downtime End must be after Downtime Start")

		if self.actual_start_time and self.actual_end_time:
			if self.actual_end_time <= self.actual_start_time:
				frappe.throw("Actual End Time must be after Actual Start Time")

	def log_workflow_transition(self):
		if self.is_new():
			return

		previous = self.get_doc_before_save()
		if not previous or previous.get("workflow_state") == self.workflow_state:
			return

		self.append(
			"approval_log",
			{
				"stage": self.workflow_state,
				"previous_stage": previous.get("workflow_state"),
				"action_by": frappe.session.user,
				"action_on": now_datetime(),
			},
		)


@frappe.whitelist()
def get_workgroup_owner_details(team):
	"""Return formatted owner details for the selected HD Team."""
	if not team:
		return ""

	team_doc = frappe.get_doc("HD Team", team)
	lines = []

	for member in team_doc.users or []:
		if not member.user:
			continue

		full_name = frappe.db.get_value("User", member.user, "full_name") or member.user
		email = frappe.db.get_value("User", member.user, "email") or ""
		lines.append(f"{full_name} ({email})" if email else full_name)

	if not lines:
		return f"No members assigned to workgroup {team}"

	return "\n".join(lines)
