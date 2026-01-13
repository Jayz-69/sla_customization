import frappe
from frappe.utils import now_datetime, get_datetime


# =========================================================
# ENTRY POINT (CALLED BY SCHEDULER)
# =========================================================

def run():
    """
    Scheduler entry point.
    Fetches all open tickets and evaluates SLA milestones.
    """
    tickets = get_open_category_tickets()

    for ticket in tickets:
        sla_update = get_or_create_sla_update(ticket.name)
        handle_first_response(ticket, sla_update)
        handle_resolution(ticket, sla_update)


# =========================================================
# FETCH ONLY OPEN CATEGORY TICKETS
# =========================================================

def get_open_category_tickets():
    """
    Returns HD Ticket docs where status_category = Open
    """
    names = frappe.get_all(
        "HD Ticket",
        filters={"status_category": "Open"},
        pluck="name"
    )
    return [frappe.get_doc("HD Ticket", name) for name in names]


# =========================================================
# SLA UPDATE DOC (CUSTOM DOCTYPE)
# =========================================================

def get_or_create_sla_update(ticket_name):
    """
    Fetch existing Sla Update doc or create one.
    One row per ticket.
    """
    existing = frappe.get_all(
        "Sla Update",
        filters={"ticket_id": ticket_name},
        pluck="name"
    )

    if existing:
        return frappe.get_doc("Sla Update", existing[0])

    doc = frappe.get_doc({
        "doctype": "Sla Update",
        "ticket_id": ticket_name
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return doc


# =========================================================
# ASSIGNEE EMAIL FETCH
# =========================================================

def get_ticket_assignee_email(ticket_name):
    """
    Returns email address of the first open ToDo assignee.
    """
    assignees = frappe.get_all(
        "ToDo",
        filters={
            "reference_type": "HD Ticket",
            "reference_name": ticket_name,
            "status": "Open"
        },
        pluck="allocated_to",
        limit=1
    )

    if not assignees:
        return None

    return frappe.get_value("User", assignees[0], "email")


# =========================================================
# COMMON SLA UTILITIES
# =========================================================

def get_percentage(start, due):
    """
    Calculates elapsed SLA percentage.
    """
    if not start or not due:
        return 0

    start = get_datetime(start)
    due = get_datetime(due)

    total = (due - start).total_seconds()
    if total <= 0:
        return 100

    elapsed = (now_datetime() - start).total_seconds()
    return min((elapsed / total) * 100, 100)


# =========================================================
# FIRST RESPONSE SLA HANDLER (FIXED)
# =========================================================

def handle_first_response(ticket, sla_update):
    """
    Handles 50%, 75%, 100% milestones cumulatively
    for First Response SLA.
    """
    # Stop if already responded
    if ticket.first_response_time:
        return

    pct = get_percentage(ticket.creation, ticket.response_by)

    for milestone in (50, 75, 100):
        if pct < milestone:
            continue

        field = f"fr_{milestone}_notified"
        if getattr(sla_update, field, 0):
            continue

        send_email(ticket, "first response", milestone)
        setattr(sla_update, field, 1)

    sla_update.save(ignore_permissions=True)
    frappe.db.commit()


# =========================================================
# RESOLUTION SLA HANDLER (FIXED)
# =========================================================

def handle_resolution(ticket, sla_update):
    """
    Handles 50%, 75%, 100% milestones cumulatively
    for Resolution SLA.
    """
    # Stop if already resolved
    if ticket.resolution_time:
        return

    pct = get_percentage(ticket.creation, ticket.resolution_by)

    for milestone in (50, 75, 100):
        if pct < milestone:
            continue

        field = f"res_{milestone}_notified"
        if getattr(sla_update, field, 0):
            continue

        send_email(ticket, "resolution", milestone)
        setattr(sla_update, field, 1)

    sla_update.save(ignore_permissions=True)
    frappe.db.commit()


# =========================================================
# EMAIL SENDER
# =========================================================

def send_email(ticket, sla_type, milestone):
    """
    Sends SLA notification email to assignee.
    """
    assignee_email = get_ticket_assignee_email(ticket.name)
    if not assignee_email:
        return

    # Capitalize SLA type for subject clarity
    sla_label = "First Response SLA" if sla_type == "first response" else "Resolution SLA"

    subject = (
        f"{sla_label} Alert ({milestone}%) – Ticket {ticket.name}"
    )

    if milestone == 100:
        message = (
            f"All {sla_type} time for ticket {ticket.name} has passed.<br><br>"
            "Immediate action is required."
        )
    else:
        message = (
            f"{milestone}% of {sla_type} time has passed for "
            f"ticket {ticket.name}."
        )

    frappe.sendmail(
        recipients=[assignee_email],
        subject=subject,
        message=message,
        delayed=False
    )

