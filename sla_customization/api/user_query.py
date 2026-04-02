import frappe
from frappe.utils import now_datetime
from datetime import timedelta


def get_last_seen_text(lastupdate):
    if not lastupdate:
        return "Offline"

    diff = now_datetime() - lastupdate
    minutes = int(diff.total_seconds() / 60)

    if minutes < 1:
        return "🟢 Active now"
    elif minutes < 60:
        return f"Last seen {minutes} min ago"
    else:
        hours = minutes // 60
        return f"Last seen {hours} hr ago"


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def active_user_query(doctype, txt, searchfield, start, page_len, filters):
    
    data = frappe.db.sql("""
        SELECT
            u.name,
            u.full_name,
            MAX(s.lastupdate) as lastupdate
        FROM `tabUser` u
        LEFT JOIN `tabSessions` s ON s.user = u.name
        WHERE u.enabled = 1
            AND u.user_type = 'System User'
            AND u.name NOT IN ('Guest', 'Administrator')
            AND u.name LIKE %(txt)s
        GROUP BY u.name, u.full_name
        ORDER BY lastupdate DESC
        LIMIT %(start)s, %(page_len)s
    """, {
        "txt": f"%{txt}%",
        "start": start,
        "page_len": page_len
    }, as_dict=True)

    return [[d.name, d.full_name, get_last_seen_text(d.get("lastupdate"))] for d in data]