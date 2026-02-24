import frappe
from frappe.utils import now_datetime, get_datetime

def run_state_tracking():
    """
    Handle state changes and timestamp recording - runs less frequently
    """
    # Get tickets that changed status recently
    tickets_with_status_changes = get_recently_updated_tickets()
    
    for ticket in tickets_with_status_changes:
        sla_update = get_or_create_sla_update(ticket.name)
        
        # Record first response timestamp
        if ticket.status == "In-Progress" and not sla_update.first_responded_on:
            sla_update.first_responded_on = now_datetime()
            sla_update.save(ignore_permissions=True)
        
        # Record resolution timestamp
        if ticket.resolution_date and not sla_update.resolution_date:
            sla_update.resolution_date = get_datetime(ticket.resolution_date)
            sla_update.save(ignore_permissions=True)
    
    # Close resolved tickets after 2 days
    close_old_resolved_tickets()
    
    frappe.db.commit()

def get_recently_updated_tickets():
    """
    Get tickets updated in last 10 minutes to avoid processing all tickets
    """
    from frappe.utils import add_to_date
    
    ten_minutes_ago = add_to_date(now_datetime(), minutes=-10)
    
    ticket_names = frappe.get_all(
        "HD Ticket",
        filters={
            "modified": [">=", ten_minutes_ago],
            "status": ["in", ["Open", "In-Progress", "Resolved", "Closed"]]
        },
        pluck="name"
    )
    
    return [frappe.get_doc("HD Ticket", name) for name in ticket_names]

def get_or_create_sla_update(ticket_name):
    """
    Get or create SLA Update record efficiently
    """
    existing = frappe.db.get_value("Sla Update", {"ticket_id": ticket_name}, "name")
    
    if existing:
        return frappe.get_doc("Sla Update", existing)
    
    doc = frappe.get_doc({
        "doctype": "Sla Update",
        "ticket_id": ticket_name
    })
    doc.insert(ignore_permissions=True)
    return doc

def close_old_resolved_tickets():
    """
    Close tickets that have been resolved for more than 2 days
    """
    from frappe.utils import add_days
    
    two_days_ago = add_days(now_datetime(), -2)
    
    resolved_tickets = frappe.get_all(
        "HD Ticket",
        filters={
            "status": "Resolved",
            "resolution_date": ["<=", two_days_ago]
        },
        pluck="name"
    )
    
    for ticket_name in resolved_tickets:
        frappe.db.set_value("HD Ticket", ticket_name, "status", "Closed")
    
    if resolved_tickets:
        frappe.db.commit()