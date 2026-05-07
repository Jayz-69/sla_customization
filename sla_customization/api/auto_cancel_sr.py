import frappe

def handle_incident_conversion_logs(doc, method=None):
    if doc.get("custom_is_incident_conversion") and doc.get("custom_sr_id"):
        # 1. Fetch the Service Request (SR) Document
        sr_doc = frappe.get_doc("HD Ticket", doc.custom_sr_id)
        
        # 2. Generate Links safely
        doc_link = frappe.utils.get_link_to_form("HD Ticket", doc.name)
        sr_doc_link = frappe.utils.get_link_to_form("HD Ticket", sr_doc.name)

        # 3. Add Comment to the old SR and update status
        sr_doc.add_comment(
            comment_type="Info",
            text=f"This Request is Cancelled and corresponding Incident has been created: {doc_link}"
        )
        
        # Use db_set for workflow_state to avoid triggering unwanted validations/hooks
        sr_doc.db_set("workflow_state", "Cancelled")
        sr_doc.db_set("status", "Cancelled")

        # 4. Add Comment to the new Incident (Current Doc)
        # We use doc.add_comment instead of frappe.get_doc({"doctype": "Comment"...}) 
        # because it is the standard Frappe way.
        doc.add_comment(
            comment_type="Info",
            text=f"This Incident is created for the corresponding service request: {sr_doc_link}"
        )

    