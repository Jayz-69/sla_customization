import frappe
from frappe.utils import now_datetime
from datetime import timedelta


# #def get_last_seen_text(lastupdate):
#     if not lastupdate:
#         return "Offline"

#     diff = now_datetime() - lastupdate
#     minutes = int(diff.total_seconds() / 60)

#     if minutes < 1:
#         return "🟢 Active now"
#     elif minutes < 60:
#         return f"Last seen {minutes} min ago"
#     else:
#         hours = minutes // 60
#         return f"Last seen {hours} hr ago"


# @frappe.whitelist()
# @frappe.validate_and_sanitize_search_inputs
# #def active_user_query(doctype, txt, searchfield, start, page_len, filters):
	
#     data = frappe.db.sql("""
#         SELECT
#             u.name,
#             u.full_name,
#             MAX(s.lastupdate) as lastupdate
#         FROM `tabUser` u
#         LEFT JOIN `tabSessions` s ON s.user = u.name
#         WHERE u.enabled = 1
#             AND u.user_type = 'System User'
#             AND u.name NOT IN ('Guest', 'Administrator')
#             AND u.name LIKE %(txt)s
#         GROUP BY u.name, u.full_name
#         ORDER BY lastupdate DESC
#         LIMIT %(start)s, %(page_len)s
#     """, {
#         "txt": f"%{txt}%",
#         "start": start,
#         "page_len": page_len
#     }, as_dict=True)

#     return [[d.name, d.full_name, get_last_seen_text(d.get("lastupdate"))] for d in data]

import frappe
from frappe.utils import now_datetime, get_datetime
import datetime

@frappe.whitelist()
def active_user_query(doctype, txt, searchfield, start, page_len, filters):
	limit = int(page_len or 20)
	offset = int(start or 0)
	frappe.log_error(str(filters))
	workgroup = frappe.get_value("Email Account",filters["email_account"],"custom_workgroup")
	user_list = frappe.get_all("HD Team Member", 
                           filters={"parent": workgroup}, 
                           pluck="user")

	data = frappe.db.sql(f"""
		SELECT 
			u.name, 
			u.full_name,
			u.last_login,
			(SELECT COUNT(*) FROM `tabSessions` WHERE user = u.name) as has_session
		FROM `tabUser` u
		WHERE u.enabled = 1
			AND u.name IN %(user_list)s
			AND u.user_type = 'System User'
			AND u.name NOT IN ('Guest', 'Administrator')
			AND (u.name LIKE %(txt)s OR u.full_name LIKE %(txt)s)
		ORDER BY has_session DESC, u.last_login DESC
		LIMIT {limit} OFFSET {offset}
	""", {"user_list":user_list,"txt": f"%{txt}%"}, as_dict=True)

	result = []
	for d in data:
		if d.has_session > 0:
			status = "🟢 Active"
		else:
			# Safely convert to datetime object
			last_login = get_datetime(d.last_login) if d.last_login else None
			status = get_last_seen(last_login)
			
		result.append([d.name, f"{d.full_name} ({status})"])
	return result

def get_last_seen(last_login):
	# Ensure last_login is a valid datetime object before math
	if not last_login or not isinstance(last_login, (datetime.datetime, datetime.date)):
		return "⚪ Never logged in"
	
	# Force now_datetime to be timezone-naive if last_login is naive to prevent mismatch
	now = now_datetime()
	if last_login.tzinfo is None and now.tzinfo is not None:
		now = now.replace(tzinfo=None)

	diff = now - last_login
	seconds = diff.total_seconds()
	
	if seconds < 3600:
		return f"Last seen {int(seconds // 60)}m ago"
	elif seconds < 86400:
		return f"Last seen {int(seconds // 3600)}h ago"
	else:
		return f"Last seen {int(seconds // 86400)}d ago"

