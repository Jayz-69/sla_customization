import frappe

SR_TO_INCIDENT_RESET_FIELDS = [
    "custom_logged_time", "sla", "response_by", "resolution_by",
    "service_level_agreement_creation", "custom_response_sla_breach",
    "custom_resolution_sla_breach", "custom_response_sla_failure_reason",
    "custom_resolution_sla_failure_reason"
]

def validate_incident_conversion(doc, method=None):
    # --- SAFEGUARD: Prevent background email updates from crashing on empty descriptions ---
    if not doc.get("description"):
        doc.description = doc.get("subject") or "No Description Provided via Email Sync"

    if not doc.get("custom_is_incident_conversion") or not doc.get("custom_sr_id"):
        return

    if doc.is_new():
        for field in SR_TO_INCIDENT_RESET_FIELDS:
            doc.set(field, None)
        return

    sr_doc = frappe.get_doc("HD Ticket", doc.custom_sr_id)
    if sr_doc.status != "New":
        frappe.throw("Only Service Requests with status <b>New</b> can be converted to Incidents")

    for field in SR_TO_INCIDENT_RESET_FIELDS:
        doc.set(field, None)


def reset_fields_on_entry_type_change(doc, method=None):
    # --- SAFEGUARD: Prevent background email updates from crashing on empty descriptions ---
    if not doc.get("description"):
        doc.description = doc.get("subject") or "No Description Provided via Email Sync"

    if doc.get("custom_entry_type") != "Incident":
        return

    if doc.is_new():
        for field in SR_TO_INCIDENT_RESET_FIELDS:
            doc.set(field, None)
        doc.set("custom_sr_id", None)
        doc.set("custom_is_incident_conversion", 0)
        return

    doc_before = doc.get_doc_before_save()
    if not doc_before or doc_before.get("custom_entry_type") == "Incident":
        return

    for field in SR_TO_INCIDENT_RESET_FIELDS:
        doc.set(field, None)

    doc.set("custom_sr_id", None)
    doc.set("custom_is_incident_conversion", 0)
