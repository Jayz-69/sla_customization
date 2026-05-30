import secrets
from datetime import timedelta
from urllib.parse import quote, unquote_plus

import frappe
from frappe.model.workflow import get_transitions, get_workflow, has_approval_access
from frappe.utils import get_url, now_datetime

TOKEN_VALIDITY_HOURS = 72

# When a Change Record enters these states, email approvers for pending actions.
STATE_EMAIL_CONFIG = {
	"Initial Authorization": {
		"subject": "Change Record {name} — Authorization required",
		"actions": ["Approve", "Reject"],
		"roles": ["Agent Manager"],
	},
	"Requested": {
		"subject": "Change Record {name} — Ready for authorization",
		"actions": ["Send for Authorization"],
		"roles": ["Agent Manager", "Agent"],
	},
}


def on_change_record_update(doc, method=None):
	if doc.is_new():
		return

	previous = doc.get_doc_before_save()
	if not previous or previous.get("workflow_state") == doc.workflow_state:
		return

	send_approval_emails(doc)


def send_approval_emails(doc):
	config = STATE_EMAIL_CONFIG.get(doc.workflow_state)
	if not config:
		return

	recipients = get_recipients(doc, config.get("roles", []))
	if not recipients:
		return

	for user_email in recipients:
		token = create_email_token(doc.name, user_email)
		send_approval_email(doc, user_email, token, config)


def get_recipients(doc, roles):
	emails = set()

	team_emails = _get_workgroup_member_emails(doc.owner_workgroup, roles)
	emails.update(team_emails)

	if not emails:
		emails.update(_get_role_user_emails(roles))

	return sorted(emails)


def _get_workgroup_member_emails(team, roles):
	if not team:
		return []

	emails = []
	team_doc = frappe.get_doc("HD Team", team)

	for member in team_doc.users or []:
		if not member.user:
			continue

		user_roles = frappe.get_roles(member.user)
		if roles and not set(roles).intersection(user_roles):
			continue

		email = frappe.db.get_value("User", member.user, "email")
		if email:
			emails.append(email)

	return emails


def _get_role_user_emails(roles):
	if not roles:
		return []

	user_names = frappe.get_all(
		"Has Role",
		filters={"role": ["in", roles], "parenttype": "User"},
		pluck="parent",
	)

	emails = []
	for user in user_names:
		if not frappe.db.get_value("User", user, "enabled"):
			continue
		email = frappe.db.get_value("User", user, "email")
		if email:
			emails.append(email)

	return emails


def create_email_token(change_record, user_email):
	user = frappe.db.get_value("User", {"email": user_email}, "name")
	if not user:
		frappe.throw(f"No user found for email {user_email}")

	_invalidate_unused_tokens(change_record, user)

	token = secrets.token_urlsafe(32)
	doc = frappe.get_doc(
		{
			"doctype": "Change Record Email Token",
			"change_record": change_record,
			"user": user,
			"token": token,
			"expires_on": now_datetime() + timedelta(hours=TOKEN_VALIDITY_HOURS),
		}
	)
	doc.insert(ignore_permissions=True)
	return token


def _invalidate_unused_tokens(change_record, user):
	frappe.db.sql(
		"""
		UPDATE `tabChange Record Email Token`
		SET is_used = 1, used_on = %s
		WHERE change_record = %s AND user = %s AND is_used = 0
		""",
		(now_datetime(), change_record, user),
	)


def send_approval_email(doc, recipient, token, config):
	subject = config["subject"].format(name=doc.name)
	actions = config.get("actions", [])
	action_links = []

	for action in actions:
		url = get_email_action_url(token, action)
		if action == "Reject":
			color = "#dc3545"
		elif action == "Approve":
			color = "#28a745"
		else:
			color = "#007bff"
		action_links.append(
			f'<a href="{url}" style="display:inline-block;margin:8px 12px 8px 0;padding:10px 18px;'
			f"background:{color};color:#fff;text-decoration:none;border-radius:4px;font-weight:600;"
			f'">{action}</a>'
		)

	record_url = get_url(f"/app/change-record/{doc.name}")
	requestor = frappe.db.get_value("User", doc.requestor, "full_name") or doc.requestor

	message = f"""
	<p>A Change Record requires your action.</p>
	<table style="border-collapse:collapse;margin:16px 0;">
		<tr><td style="padding:4px 12px 4px 0;"><strong>Record</strong></td><td>{doc.name}</td></tr>
		<tr><td style="padding:4px 12px 4px 0;"><strong>Status</strong></td><td>{doc.workflow_state}</td></tr>
		<tr><td style="padding:4px 12px 4px 0;"><strong>Requestor</strong></td><td>{requestor}</td></tr>
		<tr><td style="padding:4px 12px 4px 0;"><strong>Category</strong></td><td>{doc.category or ""}</td></tr>
		<tr><td style="padding:4px 12px 4px 0;"><strong>Change Type</strong></td><td>{doc.change_type or ""}</td></tr>
	</table>
	<p><strong>Actions</strong></p>
	<p>{"".join(action_links)}</p>
	<p>Or <a href="{record_url}">open the Change Record in Helpdesk</a>.</p>
	<p style="color:#666;font-size:12px;">Links expire in {TOKEN_VALIDITY_HOURS} hours and can only be used once.</p>
	"""

	frappe.sendmail(
		recipients=[recipient],
		subject=subject,
		message=message,
		delayed=False,
	)


def get_email_action_url(token, action):
	return get_url(
		"/api/method/sla_customization.api.change_record_email.handle_email_action"
		f"?token={quote(token, safe='')}&action={quote(action, safe='')}"
	)


@frappe.whitelist(allow_guest=True)
def handle_email_action(token, action):
	action = unquote_plus(action or "")
	try:
		message = _process_email_action(token, action)
		frappe.respond_as_web_page(
			"Change Record Updated",
			message,
			indicator_color="green",
		)
	except frappe.PermissionError:
		frappe.respond_as_web_page(
			"Action Failed",
			"You do not have permission to update this Change Record.",
			indicator_color="red",
			http_status_code=403,
		)
	except Exception as exc:
		message = str(exc) or getattr(frappe.local, "message", None) or "An unexpected error occurred."
		frappe.respond_as_web_page(
			"Action Failed",
			message,
			indicator_color="red",
			http_status_code=400,
		)


def _process_email_action(token, action):
	token_doc = _get_valid_token(token)
	user = token_doc.user

	frappe.set_user(user)

	doc = frappe.get_doc("Change Record", token_doc.change_record)
	doc.reload()
	transition = _get_valid_transition(doc, action, user)

	_apply_workflow_transition(doc, transition, user)

	token_doc.is_used = 1
	token_doc.used_on = now_datetime()
	token_doc.save(ignore_permissions=True)
	frappe.db.commit()

	return f"Change Record <b>{doc.name}</b> was updated successfully.<br>Action: <b>{action}</b>"


def _get_valid_transition(doc, action, user):
	transitions = get_transitions(doc)
	allowed_actions = {t["action"] for t in transitions}

	if action not in allowed_actions:
		record_url = get_url(f"/app/change-record/{doc.name}")
		if allowed_actions:
			available = ", ".join(sorted(allowed_actions))
			frappe.throw(
				f"This approval link is no longer valid. The Change Record is currently in "
				f"<b>{doc.workflow_state}</b> state.<br><br>"
				f"Available actions now: {available}.<br><br>"
				f"<a href='{record_url}'>Open the Change Record in Helpdesk</a>."
			)

		frappe.throw(
			f"You are not allowed to perform <b>{action}</b> on this Change Record.<br><br>"
			f"Current state: <b>{doc.workflow_state}</b>.<br><br>"
			f"<a href='{record_url}'>Open the Change Record in Helpdesk</a>."
		)

	transition = next(t for t in transitions if t["action"] == action)

	if not has_approval_access(user, doc, transition):
		frappe.throw("Self approval is not allowed for this Change Record.")

	return transition


def _apply_workflow_transition(doc, transition, user):
	workflow = get_workflow(doc.doctype)
	next_state = next(d for d in workflow.states if d.state == transition["next_state"])

	doc.set(workflow.workflow_state_field, transition["next_state"])

	if next_state.update_field:
		doc.set(next_state.update_field, next_state.update_value)

	doc.save(ignore_permissions=True)
	doc.add_comment("Workflow", transition["next_state"])


def _get_valid_token(token):
	if not token:
		frappe.throw("Invalid or missing token.")

	token_name = frappe.db.get_value("Change Record Email Token", {"token": token}, "name")
	if not token_name:
		frappe.throw("Invalid or expired approval link.")

	token_doc = frappe.get_doc("Change Record Email Token", token_name)

	if token_doc.is_used:
		frappe.throw("This approval link has already been used.")

	if token_doc.expires_on and token_doc.expires_on < now_datetime():
		frappe.throw("This approval link has expired.")

	return token_doc
