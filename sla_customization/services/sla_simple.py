import frappe
from frappe.utils import now_datetime, get_datetime

def check_50_percent_sla():
    """Worker for 50% SLA alerts"""
    process_milestone_alerts(50)

def check_75_percent_sla():
    """Worker for 75% SLA alerts"""
    process_milestone_alerts(75)

def check_100_percent_sla():
    """Worker for 100% SLA alerts"""
    process_milestone_alerts(100)

def process_milestone_alerts(milestone):
    """Process alerts for specific milestone"""
    tickets = get_tickets_for_milestone(milestone)
    
    for ticket in tickets:
        # Check first response SLA
        if not ticket.first_response_time and ticket.response_by:
            if check_milestone_reached(ticket, milestone, 'first_response'):
                send_alert(ticket, milestone, 'first_response')
                mark_notified(ticket.name, f'fr_{milestone}_notified')
        
        # Check resolution SLA
        if not ticket.resolution_time and ticket.resolution_by:
            if check_milestone_reached(ticket, milestone, 'resolution'):
                send_alert(ticket, milestone, 'resolution')
                mark_notified(ticket.name, f'res_{milestone}_notified')

def get_tickets_for_milestone(milestone):
    """Get tickets that might have reached this milestone"""
    return frappe.db.sql(f"""
        SELECT 
            t.name, t.creation, t.response_by, t.resolution_by,
            t.first_response_time, t.resolution_time,
            COALESCE(s.fr_{milestone}_notified, 0) as fr_{milestone}_notified,
            COALESCE(s.res_{milestone}_notified, 0) as res_{milestone}_notified
        FROM `tabHD Ticket` t
        LEFT JOIN `tabSla Update` s ON t.name = s.ticket_id
        WHERE t.status IN ('Open', 'In-Progress')
        AND (
            (s.fr_{milestone}_notified = 0 AND t.first_response_time IS NULL)
            OR (s.res_{milestone}_notified = 0 AND t.resolution_time IS NULL)
        )
    """, as_dict=True)

def check_milestone_reached(ticket, milestone, sla_type):
    """Check if milestone percentage is reached"""
    current_time = now_datetime()
    start_time = get_datetime(ticket.creation)
    
    if sla_type == 'first_response':
        due_time = get_datetime(ticket.response_by)
    else:
        due_time = get_datetime(ticket.resolution_by)
    
    if not due_time:
        return False
    
    total_seconds = (due_time - start_time).total_seconds()
    if total_seconds <= 0:
        return milestone == 100
    
    elapsed_seconds = (current_time - start_time).total_seconds()
    percentage = (elapsed_seconds / total_seconds) * 100
    
    return percentage >= milestone

def send_alert(ticket, milestone, sla_type):
    """Send SLA alert email"""
    from sla_customization.services.sla_engine import get_ticket_assignee_email
    
    email = get_ticket_assignee_email(ticket.name)
    if not email:
        return
    
    subject = f"SLA Alert ({milestone}%) - Ticket {ticket.name}"
    
    if milestone == 100:
        message = f"SLA BREACH: {sla_type} time exceeded for ticket {ticket.name}"
    else:
        message = f"{milestone}% of {sla_type} time passed for ticket {ticket.name}"
    
    # Use background job for email to avoid blocking
    frappe.enqueue(
        'frappe.core.doctype.communication.email.sendmail_to_system_users',
        recipients=[email],
        subject=subject,
        message=message,
        queue='short'
    )

def mark_notified(ticket_name, field_name):
    """Mark milestone as notified"""
    sla_update = frappe.db.get_value('Sla Update', {'ticket_id': ticket_name}, 'name')
    
    if not sla_update:
        doc = frappe.get_doc({
            'doctype': 'Sla Update',
            'ticket_id': ticket_name
        })
        doc.insert(ignore_permissions=True)
        sla_update = doc.name
    
    frappe.db.set_value('Sla Update', sla_update, field_name, 1)
    frappe.db.commit()