import frappe

def validate_incident_conversion(doc, method=None):
    # Check if this is an incident conversion
    if doc.get("custom_is_incident_conversion"):
        
        if doc.get("custom_sr_id"):
            # Fetch the Service Request document
            sr_doc = frappe.get_doc("HD Ticket", doc.custom_sr_id)
            
            # Validation: Only allow conversion if SR status is 'New'
            if sr_doc.status != "New":
                frappe.throw("Only Service Requests with status <b>New</b> can be converted to Incidents")
            
            # Resetting SLA and log fields for the new Incident
            fields_to_reset = [
                "custom_logged_time", "sla", "response_by", "resolution_by",
                "service_level_agreement_creation", "custom_response_sla_breach",
                "custom_resolution_sla_breach", "custom_response_sla_failure_reason",
                "custom_resolution_sla_failure_reason"
            ]
            
            for field in fields_to_reset:
                doc.set(field, None) # Using .set is safer for backend docs