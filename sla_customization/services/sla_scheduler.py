import frappe
from frappe.utils import now_datetime, get_datetime, add_to_date
from datetime import timedelta

def run_sla_alerts():
    """
    Optimized SLA scheduler - processes only tickets nearing milestones
    """
    current_time = now_datetime()
    
    # Process tickets in batches to avoid memory issues
    batch_size = 100
    
    # Get tickets that need immediate attention (next 2 minutes)
    urgent_tickets = get_tickets_near_milestones(current_time, minutes=2)
    
    for batch_start in range(0, len(urgent_tickets), batch_size):
        batch = urgent_tickets[batch_start:batch_start + batch_size]
        process_ticket_batch(batch, current_time)

def get_tickets_near_milestones(current_time, minutes=2):
    """
    Get only tickets that are approaching SLA milestones in next few minutes
    """
    # Calculate time window
    future_time = add_to_date(current_time, minutes=minutes)
    
    # Query for tickets with SLA times in the near future
    tickets = frappe.db.sql("""
        SELECT 
            t.name,
            t.creation,
            t.response_by,
            t.resolution_by,
            t.status,
            t.first_response_time,
            t.resolution_time,
            s.fr_50_notified,
            s.fr_75_notified, 
            s.fr_100_notified,
            s.res_50_notified,
            s.res_75_notified,
            s.res_100_notified
        FROM `tabHD Ticket` t
        LEFT JOIN `tabSla Update` s ON t.name = s.ticket_id
        WHERE t.status IN ('Open', 'In-Progress')
        AND (
            (t.response_by BETWEEN %s AND %s AND t.first_response_time IS NULL)
            OR (t.resolution_by BETWEEN %s AND %s AND t.resolution_time IS NULL)
        )
    """, (current_time, future_time, current_time, future_time), as_dict=True)
    
    return tickets

def process_ticket_batch(tickets, current_time):
    """
    Process a batch of tickets for SLA alerts
    """
    alerts_to_send = []
    
    for ticket in tickets:
        # Check first response SLA
        if not ticket.first_response_time and ticket.response_by:
            alerts_to_send.extend(
                check_sla_milestones(ticket, current_time, 'first_response')
            )
        
        # Check resolution SLA  
        if not ticket.resolution_time and ticket.resolution_by:
            alerts_to_send.extend(
                check_sla_milestones(ticket, current_time, 'resolution')
            )
    
    # Send alerts asynchronously
    if alerts_to_send:
        frappe.enqueue(
            'sla_customization.services.sla_scheduler.send_batch_alerts',
            alerts=alerts_to_send,
            queue='short'
        )

def check_sla_milestones(ticket, current_time, sla_type):
    """
    Check which milestones need alerts
    """
    alerts = []
    
    if sla_type == 'first_response':
        due_time = get_datetime(ticket.response_by)
        prefix = 'fr'
    else:
        due_time = get_datetime(ticket.resolution_by)
        prefix = 'res'
    
    start_time = get_datetime(ticket.creation)
    total_seconds = (due_time - start_time).total_seconds()
    elapsed_seconds = (current_time - start_time).total_seconds()
    
    if total_seconds <= 0:
        return alerts
    
    percentage = min((elapsed_seconds / total_seconds) * 100, 100)
    
    # Check each milestone
    for milestone in [50, 75, 100]:
        field_name = f"{prefix}_{milestone}_notified"
        
        if percentage >= milestone and not ticket.get(field_name):
            alerts.append({
                'ticket_name': ticket.name,
                'sla_type': sla_type,
                'milestone': milestone,
                'field_name': field_name
            })
    
    return alerts

def send_batch_alerts(alerts):
    """
    Send alerts in batch and update notification flags
    """
    from sla_customization.services.sla_engine import get_ticket_assignee_email
    
    # Group alerts by assignee to reduce emails
    assignee_alerts = {}
    
    for alert in alerts:
        email = get_ticket_assignee_email(alert['ticket_name'])
        if email:
            if email not in assignee_alerts:
                assignee_alerts[email] = []
            assignee_alerts[email].append(alert)
    
    # Send consolidated emails
    for email, user_alerts in assignee_alerts.items():
        send_consolidated_email(email, user_alerts)
    
    # Update notification flags
    update_notification_flags(alerts)

def send_consolidated_email(email, alerts):
    """
    Send one email with multiple ticket alerts
    """
    if len(alerts) == 1:
        alert = alerts[0]
        subject = f"SLA Alert ({alert['milestone']}%) - Ticket {alert['ticket_name']}"
        message = f"{alert['milestone']}% of {alert['sla_type']} time has passed for ticket {alert['ticket_name']}."
    else:
        subject = f"SLA Alerts - {len(alerts)} tickets require attention"
        message = "The following tickets require your attention:<br><br>"
        for alert in alerts:
            message += f"• Ticket {alert['ticket_name']}: {alert['milestone']}% {alert['sla_type']} SLA<br>"
    
    frappe.sendmail(
        recipients=[email],
        subject=subject,
        message=message,
        delayed=True  # Use email queue
    )

def update_notification_flags(alerts):
    """
    Update notification flags in batch
    """
    updates_by_ticket = {}
    
    for alert in alerts:
        ticket_name = alert['ticket_name']
        if ticket_name not in updates_by_ticket:
            updates_by_ticket[ticket_name] = {}
        updates_by_ticket[ticket_name][alert['field_name']] = 1
    
    for ticket_name, updates in updates_by_ticket.items():
        # Get or create SLA Update record
        sla_update = frappe.db.get_value('Sla Update', {'ticket_id': ticket_name}, 'name')
        
        if not sla_update:
            doc = frappe.get_doc({
                'doctype': 'Sla Update',
                'ticket_id': ticket_name
            })
            doc.insert(ignore_permissions=True)
            sla_update = doc.name
        
        # Update flags
        frappe.db.set_value('Sla Update', sla_update, updates)
    
    frappe.db.commit()