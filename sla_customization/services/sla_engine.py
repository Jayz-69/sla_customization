import frappe
from frappe.utils import now_datetime, get_datetime, add_days


# =========================================================
# ENTRY POINT (CALLED BY SCHEDULER)
# =========================================================

def run():
    """
    Scheduler entry point.
    """

    # ------------------------------------------------------------------
    # 1. STATE TRACKING (timestamps must see all relevant statuses)
    # ------------------------------------------------------------------
    state_tickets = get_tickets_by_status(
        ["Open", "In-Progress", "Resolved", "Closed"]
    )

    for ticket in state_tickets:
        sla_update = get_or_create_sla_update(ticket.name)
        record_first_response_time(ticket, sla_update)
        record_resolution_time(ticket, sla_update)

    # ------------------------------------------------------------------
    # 2. FIRST RESPONSE SLA → ONLY Open tickets
    # ------------------------------------------------------------------
    open_tickets = get_tickets_by_status(["Open"])
    for ticket in open_tickets:
        sla_update = get_or_create_sla_update(ticket.name)
        handle_first_response(ticket, sla_update)

    # ------------------------------------------------------------------
    # 3. RESOLUTION SLA → Open + In-Progress tickets
    # ------------------------------------------------------------------
    resolution_tickets = get_tickets_by_status(["Open", "In-Progress"])
    for ticket in resolution_tickets:
        sla_update = get_or_create_sla_update(ticket.name)
        handle_resolution(ticket, sla_update)

    close_resolved_tickets()


# =========================================================
# FETCH TICKETS BY STATUS
# =========================================================

def get_tickets_by_status(status_list):
    """
    Fetch HD Ticket docs by status list.
    """
    names = frappe.get_all(
        "HD Ticket",
        filters={"status": ["in", status_list]},
        pluck="name"
    )
    return [frappe.get_doc("HD Ticket", name) for name in names]


# =========================================================
# SLA UPDATE DOC (CUSTOM DOCTYPE)
# =========================================================

def get_or_create_sla_update(ticket_name):
    """
    Fetch existing Sla Update doc or create one.
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
# STATE-BASED TIMESTAMP RECORDING
# =========================================================

def record_first_response_time(ticket, sla_update):
    """
    Record First Responded On when ticket enters In-Progress.
    """
    if (
        ticket.status == "In-Progress"
        and not sla_update.first_responded_on
    ):
        sla_update.first_responded_on = now_datetime()
        sla_update.save(ignore_permissions=True)
        frappe.db.commit()


def record_resolution_time(ticket, sla_update):
    """
    Copy Resolution Date from HD Ticket once it appears.
    """
    if (
        ticket.resolution_date
        and not sla_update.resolution_date
    ):
        sla_update.resolution_date = get_datetime(ticket.resolution_date)
        sla_update.save(ignore_permissions=True)
        frappe.db.commit()


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
# FIRST RESPONSE SLA HANDLER
# =========================================================

def handle_first_response(ticket, sla_update):
    """
    Handles 50%, 75%, 100% milestones for First Response SLA.
    """
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
# RESOLUTION SLA HANDLER
# =========================================================

def handle_resolution(ticket, sla_update):
    """
    Handles 50%, 75%, 100% milestones for Resolution SLA.
    """
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

def close_resolved_tickets():
    resolved = frappe.get_all("HD Ticket",filters={"status":"Resolved"},pluck = "name")
    for name in resolved:
        doc = frappe.get_doc("HD Ticket",name)
        if add_days(doc.resolution_date,2) < now_datetime():
            doc.status = "Closed"
            doc.save()
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

    sla_label = (
        "First Response SLA"
        if sla_type == "first response"
        else "Resolution SLA"
    )

    subject = f"{sla_label} Alert ({milestone}%) – Ticket {ticket.name}"

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
