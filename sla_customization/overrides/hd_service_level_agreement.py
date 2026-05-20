from frappe.model.document import Document
from frappe.utils import now_datetime

from helpdesk.helpdesk.doctype.hd_service_level_agreement.hd_service_level_agreement import (
    HDServiceLevelAgreement,
)


class CustomHDServiceLevelAgreement(HDServiceLevelAgreement):

    def handle_new(self, doc: Document):
        if doc.is_new():
            creation = doc.get("custom_logged_time") or now_datetime()
            doc.service_level_agreement_creation = creation
            doc.priority = doc.priority or self.default_priority
            return
        if doc.has_value_changed("custom_logged_time") and doc.get("custom_logged_time"):
            doc.service_level_agreement_creation = doc.get("custom_logged_time")
