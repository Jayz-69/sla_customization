# Copyright (c) 2026, Jay Anjarlekar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ServiceRequestCronAutomation(Document):
    def on_update(self):
        frappe.log_error("Workiasgasd")
        if self.docstatus != 1:
            return
        if frappe.db.exists("Scheduled Job Type", self.custom_job_name):
            job = frappe.get_doc("Scheduled Job Type", self.custom_job_name)
        else:
            job = frappe.new_doc("Scheduled Job Type")
            job.name = self.custom_job_name

        job.method = "sla_customization.services.service_request_automation.create_service_requests" # The SAME function for everyone
        job.frequency = "Cron"
        job.cron_format = self.custom_job_time_cron
        job.stopped = 0
        job.arguments = self.custom_service_requests
        job.save(ignore_permissions=True)


    def on_update_after_submit(self):
        frappe.log_error("Workiasgasd")
        if self.docstatus != 1:
            return
        if frappe.db.exists("Scheduled Job Type", self.custom_job_name):
            job = frappe.get_doc("Scheduled Job Type", self.custom_job_name)
        else:
            job = frappe.new_doc("Scheduled Job Type")
            job.name = self.custom_job_name

        job.method = "sla_customization.services.service_request_automation.create_service_requests"
        job.frequency = "Cron"
        job.cron_format = self.custom_job_time_cron
        job.stopped = 0
        job.arguments = self.custom_service_requests
        job.save(ignore_permissions=True)
