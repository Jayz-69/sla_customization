import frappe

# SLA Configuration - easily adjustable
SLA_CONFIG = {
    # Priority levels based on SLA duration (in minutes)
    'priority_levels': {
        'critical': {'max_minutes': 15, 'check_frequency': 2},  # Check every 2 minutes
        'high': {'max_minutes': 30, 'check_frequency': 5},     # Check every 5 minutes  
        'medium': {'max_minutes': 60, 'check_frequency': 10},  # Check every 10 minutes
        'low': {'max_minutes': 240, 'check_frequency': 30}     # Check every 30 minutes
    },
    
    # Milestone percentages
    'milestones': [50, 75, 100],
    
    # Email settings
    'email_settings': {
        'batch_size': 50,           # Max tickets per batch
        'consolidate_emails': True,  # Send one email per assignee
        'immediate_critical': True,  # Send critical alerts immediately
        'use_email_queue': True     # Use delayed email sending
    },
    
    # Performance settings
    'performance': {
        'batch_size': 100,          # Tickets processed per batch
        'max_tickets_per_run': 500, # Maximum tickets to process in one run
        'lookahead_minutes': 2      # How far ahead to look for milestones
    }
}

def get_sla_config():
    """
    Get SLA configuration with site-specific overrides
    """
    # Check for site-specific configuration
    site_config = frappe.get_site_config().get('sla_customization', {})
    
    # Merge with default config
    config = SLA_CONFIG.copy()
    if site_config:
        config.update(site_config)
    
    return config

def get_priority_for_sla_minutes(sla_minutes):
    """
    Determine priority level based on SLA duration
    """
    config = get_sla_config()
    
    for priority, settings in config['priority_levels'].items():
        if sla_minutes <= settings['max_minutes']:
            return priority
    
    return 'low'

def should_process_priority(priority, current_minute):
    """
    Check if this priority level should be processed at current time
    """
    config = get_sla_config()
    frequency = config['priority_levels'][priority]['check_frequency']
    
    return current_minute % frequency == 0

def get_milestone_check_times(sla_start, sla_end):
    """
    Calculate exact times when milestone checks should occur
    """
    from frappe.utils import get_datetime
    
    start_time = get_datetime(sla_start)
    end_time = get_datetime(sla_end)
    total_duration = end_time - start_time
    
    config = get_sla_config()
    milestone_times = {}
    
    for milestone in config['milestones']:
        milestone_time = start_time + (total_duration * milestone / 100)
        milestone_times[milestone] = milestone_time
    
    return milestone_times

def get_email_template(sla_type, milestone, ticket_count=1):
    """
    Get email template based on alert type
    """
    if milestone == 100:
        if ticket_count == 1:
            return {
                'subject': f'🚨 SLA BREACH - Ticket requires immediate attention',
                'template': 'sla_breach_single'
            }
        else:
            return {
                'subject': f'🚨 SLA BREACH - {ticket_count} tickets require immediate attention', 
                'template': 'sla_breach_multiple'
            }
    else:
        if ticket_count == 1:
            return {
                'subject': f'SLA Alert ({milestone}%) - Action required',
                'template': 'sla_warning_single'
            }
        else:
            return {
                'subject': f'SLA Alerts - {ticket_count} tickets need attention',
                'template': 'sla_warning_multiple'
            }

def log_sla_performance(operation, duration, ticket_count):
    """
    Log performance metrics for monitoring
    """
    frappe.logger().info(f"SLA {operation}: {duration:.2f}s for {ticket_count} tickets")
    
    # Store in custom log if needed for analysis
    if frappe.db.exists('DocType', 'SLA Performance Log'):
        frappe.get_doc({
            'doctype': 'SLA Performance Log',
            'operation': operation,
            'duration': duration,
            'ticket_count': ticket_count,
            'timestamp': frappe.utils.now_datetime()
        }).insert(ignore_permissions=True)