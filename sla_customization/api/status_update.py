import frappe 
def update_ticket_status_logic(doc, method=None): 
    # Logic to automatically update status based on custom fields 
    if doc.get("custom_cancellation_remarks"): 
        doc.status = "Cancelled"
