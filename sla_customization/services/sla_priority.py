import frappe
from frappe.utils import now_datetime, get_datetime, add_to_date
from datetime import timedelta

def run_priority_sla_check():
    """
    Priority-based SLA checking - processes tickets based on urgency
    """
    current_time = now_datetime()
    
    # Process high priority tickets first (15min SLA)
    process_priority_tickets(current_time, max_sla_minutes=15, priority='high')
    
    # Process medium priority tickets (30min+ SLA)  
    process_priority_tickets(current_time, max_sla_minutes=60, priority='medium')
    
    # Process low priority tickets (2hr+ SLA)
    process_priority_tickets(current_time, max_sla_minutes=240, priority='low')

def process_priority_tickets(current_time, max_sla_minutes, priority):
    """
    Process tickets based on SLA duration priority
    """
    # Calculate milestone times for this priority level
    milestone_times = calculate_milestone_times(max_sla_minutes)
    
    # Get tickets that need checking for this priority
    tickets = get_tickets_by_priority(current_time, max_sla_minutes, milestone_times)
    
    if not tickets:
        return
    
    alerts = []
    for ticket in tickets:
        ticket_alerts = process_single_ticket(ticket, current_time)
        alerts.extend(ticket_alerts)
    
    # Send alerts asynchronously if any found
    if alerts:
        frappe.enqueue(
            'sla_customization.services.sla_priority.send_priority_alerts',
            alerts=alerts,
            priority=priority,
            queue='short' if priority == 'high' else 'default'
        )

def calculate_milestone_times(max_sla_minutes):
    """
    Calculate when to check for milestones based on SLA duration
    """
    # For 15min SLA: check at 7.5min, 11.25min, 15min
    # For 30min SLA: check at 15min, 22.5min, 30min  
    # For 2hr SLA: check at 1hr, 1.5hr, 2hr
    
    return {
        50: max_sla_minutes * 0.5,
        75: max_sla_minutes * 0.75, 
        100: max_sla_minutes
    }

def get_tickets_by_priority(current_time, max_sla_minutes, milestone_times):
    """
    Get tickets that need checking based on their next milestone time
    """
    # Calculate time windows for each milestone
    check_window = 1  # Check 1 minute before milestone
    
    conditions = []
    params = []
    
    for milestone, milestone_minutes in milestone_times.items():
        milestone_time = add_to_date(current_time, minutes=-milestone_minutes)
        check_time = add_to_date(milestone_time, minutes=check_window)
        
        conditions.append(f"""
            (t.creation <= %s AND t.creation >= %s 
             AND s.fr_{milestone}_notified = 0 
             AND t.first_response_time IS NULL)
        """)
        params.extend([milestone_time, check_time])
        
        conditions.append(f"""
            (t.creation <= %s AND t.creation >= %s 
             AND s.res_{milestone}_notified = 0 
             AND t.resolution_time IS NULL)
        """)
        params.extend([milestone_time, check_time])
    
    if not conditions:
        return []
    
    query = f"""
        SELECT 
            t.name, t.creation, t.response_by, t.resolution_by,
            t.status, t.first_response_time, t.resolution_time,
            COALESCE(s.fr_50_notified, 0) as fr_50_notified,
            COALESCE(s.fr_75_notified, 0) as fr_75_notified,
            COALESCE(s.fr_100_notified, 0) as fr_100_notified,
            COALESCE(s.res_50_notified, 0) as res_50_notified,
            COALESCE(s.res_75_notified, 0) as res_75_notified,
            COALESCE(s.res_100_notified, 0) as res_100_notified
        FROM `tabHD Ticket` t
        LEFT JOIN `tabSla Update` s ON t.name = s.ticket_id
        WHERE t.status IN ('Open', 'In-Progress')
        AND ({' OR '.join(conditions)})
        LIMIT 50
    """
    
    return frappe.db.sql(query, params, as_dict=True)

def process_single_ticket(ticket, current_time):
    """
    Process a single ticket for SLA alerts
    """
    alerts = []
    
    # Check first response SLA
    if not ticket.first_response_time and ticket.response_by:
        fr_alerts = check_milestone_alerts(
            ticket, current_time, 'first_response', 
            ticket.response_by, 'fr'
        )
        alerts.extend(fr_alerts)
    
    # Check resolution SLA
    if not ticket.resolution_time and ticket.resolution_by:
        res_alerts = check_milestone_alerts(
            ticket, current_time, 'resolution',
            ticket.resolution_by, 'res'
        )
        alerts.extend(res_alerts)
    
    return alerts

def check_milestone_alerts(ticket, current_time, sla_type, due_time, prefix):
    """
    Check if ticket has reached any milestone thresholds
    """
    alerts = []
    
    start_time = get_datetime(ticket.creation)
    due_datetime = get_datetime(due_time)
    
    total_seconds = (due_datetime - start_time).total_seconds()
    if total_seconds <= 0:
        return alerts
    
    elapsed_seconds = (current_time - start_time).total_seconds()
    percentage = min((elapsed_seconds / total_seconds) * 100, 100)
    
    # Check each milestone
    for milestone in [50, 75, 100]:
        field_name = f"{prefix}_{milestone}_notified"
        
        if (percentage >= milestone and 
            not ticket.get(field_name) and
            percentage < milestone + 5):  # Only alert within 5% window
            
            alerts.append({
                'ticket_name': ticket.name,
                'sla_type': sla_type,
                'milestone': milestone,
                'field_name': field_name,
                'percentage': round(percentage, 1),
                'urgency': get_urgency_level(milestone, total_seconds)
            })
    
    return alerts

def get_urgency_level(milestone, total_seconds):
    """
    Determine urgency based on milestone and total SLA time
    """
    total_minutes = total_seconds / 60
    
    if milestone == 100:
        return 'critical'
    elif milestone == 75 and total_minutes <= 30:
        return 'high'
    elif milestone == 50 and total_minutes <= 15:
        return 'high'
    else:
        return 'medium'

def send_priority_alerts(alerts, priority):
    """
    Send alerts with priority-based handling
    """
    from sla_customization.services.sla_engine import get_ticket_assignee_email
    
    # Group by urgency level
    urgent_alerts = [a for a in alerts if a['urgency'] == 'critical']
    normal_alerts = [a for a in alerts if a['urgency'] != 'critical']
    
    # Send critical alerts immediately
    if urgent_alerts:
        send_immediate_alerts(urgent_alerts)
    
    # Send normal alerts in batch
    if normal_alerts:
        send_batch_alerts(normal_alerts)
    
    # Update notification flags
    update_alert_flags(alerts)

def send_immediate_alerts(alerts):
    """
    Send critical alerts immediately without batching
    """
    from sla_customization.services.sla_engine import get_ticket_assignee_email
    
    for alert in alerts:
        email = get_ticket_assignee_email(alert['ticket_name'])
        if email:
            subject = f"🚨 URGENT: SLA Breach - Ticket {alert['ticket_name']}"
            message = f"""
            <strong>URGENT ACTION REQUIRED</strong><br><br>
            Ticket {alert['ticket_name']} has reached {alert['milestone']}% of its {alert['sla_type']} SLA.<br>
            Current progress: {alert['percentage']}%<br><br>
            Please take immediate action.
            """
            
            frappe.sendmail(
                recipients=[email],
                subject=subject,
                message=message,
                delayed=False  # Send immediately
            )

def send_batch_alerts(alerts):
    """
    Send normal priority alerts in batches
    """
    from sla_customization.services.sla_engine import get_ticket_assignee_email
    
    # Group by assignee
    assignee_alerts = {}
    for alert in alerts:
        email = get_ticket_assignee_email(alert['ticket_name'])
        if email:
            if email not in assignee_alerts:
                assignee_alerts[email] = []
            assignee_alerts[email].append(alert)
    
    # Send consolidated emails
    for email, user_alerts in assignee_alerts.items():
        if len(user_alerts) == 1:
            alert = user_alerts[0]
            subject = f"SLA Alert ({alert['milestone']}%) - Ticket {alert['ticket_name']}"
            message = f"{alert['milestone']}% of {alert['sla_type']} time has passed for ticket {alert['ticket_name']}."
        else:
            subject = f"SLA Alerts - {len(user_alerts)} tickets need attention"
            message = "Multiple tickets require your attention:<br><br>"
            for alert in user_alerts:
                message += f"• Ticket {alert['ticket_name']}: {alert['milestone']}% {alert['sla_type']} SLA ({alert['percentage']}%)<br>"
        
        frappe.sendmail(
            recipients=[email],
            subject=subject, 
            message=message,
            delayed=True
        )

def update_alert_flags(alerts):
    """
    Update notification flags efficiently
    """
    ticket_updates = {}
    
    for alert in alerts:
        ticket_name = alert['ticket_name']
        if ticket_name not in ticket_updates:
            ticket_updates[ticket_name] = {}
        ticket_updates[ticket_name][alert['field_name']] = 1
    
    # Batch update
    for ticket_name, updates in ticket_updates.items():
        sla_update = frappe.db.get_value('Sla Update', {'ticket_id': ticket_name}, 'name')
        
        if not sla_update:
            doc = frappe.get_doc({
                'doctype': 'Sla Update',
                'ticket_id': ticket_name
            })
            doc.insert(ignore_permissions=True)
            sla_update = doc.name
        
        frappe.db.set_value('Sla Update', sla_update, updates)
    
    frappe.db.commit()