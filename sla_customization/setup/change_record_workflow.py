import frappe


WORKFLOW_NAME = "Change Record Workflow"

STATES = [
	{"state": "Draft", "doc_status": "0", "allow_edit": "All", "update_field": "status", "update_value": "Draft"},
	{
		"state": "Requested",
		"doc_status": "1",
		"allow_edit": "Agent Manager",
		"update_field": "status",
		"update_value": "Requested",
	},
	{
		"state": "Initial Authorization",
		"doc_status": "1",
		"allow_edit": "Agent Manager",
		"update_field": "status",
		"update_value": "Initial Authorization",
	},
	{
		"state": "Approved",
		"doc_status": "1",
		"allow_edit": "Agent Manager",
		"update_field": "status",
		"update_value": "Approved",
	},
	{
		"state": "Rejected",
		"doc_status": "1",
		"allow_edit": "Agent",
		"update_field": "status",
		"update_value": "Draft",
	},
	{
		"state": "Implementation",
		"doc_status": "1",
		"allow_edit": "Agent",
		"update_field": "status",
		"update_value": "Implementation",
	},
	{
		"state": "Completed",
		"doc_status": "1",
		"allow_edit": "Agent Manager",
		"update_field": "status",
		"update_value": "Completed",
	},
	{
		"state": "Closed",
		"doc_status": "1",
		"allow_edit": "Agent Manager",
		"update_field": "status",
		"update_value": "Closed",
	},
]

TRANSITIONS = [
	{"state": "Draft", "action": "Submit", "next_state": "Requested", "allowed": "Agent"},
	{
		"state": "Draft",
		"action": "Submit",
		"next_state": "Requested",
		"allowed": "Agent Manager",
	},
	{
		"state": "Requested",
		"action": "Send for Authorization",
		"next_state": "Initial Authorization",
		"allowed": "Agent",
	},
	{
		"state": "Requested",
		"action": "Send for Authorization",
		"next_state": "Initial Authorization",
		"allowed": "Agent Manager",
	},
	{
		"state": "Initial Authorization",
		"action": "Approve",
		"next_state": "Approved",
		"allowed": "Agent Manager",
	},
	{
		"state": "Initial Authorization",
		"action": "Reject",
		"next_state": "Rejected",
		"allowed": "Agent Manager",
	},
	{
		"state": "Rejected",
		"action": "Resubmit",
		"next_state": "Requested",
		"allowed": "Agent",
	},
	{
		"state": "Rejected",
		"action": "Resubmit",
		"next_state": "Requested",
		"allowed": "Agent Manager",
	},
	{
		"state": "Approved",
		"action": "Start Implementation",
		"next_state": "Implementation",
		"allowed": "Agent Manager",
	},
	{
		"state": "Implementation",
		"action": "Mark Completed",
		"next_state": "Completed",
		"allowed": "Agent",
	},
	{
		"state": "Implementation",
		"action": "Mark Completed",
		"next_state": "Completed",
		"allowed": "Agent Manager",
	},
	{
		"state": "Completed",
		"action": "Close",
		"next_state": "Closed",
		"allowed": "Agent Manager",
	},
]

CUSTOM_ACTIONS = [
	"Submit",
	"Approve",
	"Reject",
	"Send for Authorization",
	"Resubmit",
	"Start Implementation",
	"Mark Completed",
	"Close",
]


def setup_change_record_workflow():
	ensure_workflow_actions()
	ensure_workflow_states()

	if frappe.db.exists("Workflow", WORKFLOW_NAME):
		frappe.delete_doc("Workflow", WORKFLOW_NAME, force=1)

	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = WORKFLOW_NAME
	workflow.document_type = "Change Record"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.send_email_alert = 0
	workflow.override_status = 0

	for state in STATES:
		workflow.append("states", state)

	for transition in TRANSITIONS:
		workflow.append(
			"transitions",
			{
				**transition,
				"allow_self_approval": 1,
			},
		)

	workflow.insert(ignore_permissions=True)
	frappe.clear_cache(doctype="Change Record")


def ensure_workflow_actions():
	for action in CUSTOM_ACTIONS:
		if not frappe.db.exists("Workflow Action Master", action):
			frappe.get_doc({"doctype": "Workflow Action Master", "workflow_action_name": action}).insert(
				ignore_permissions=True
			)


def ensure_workflow_states():
	for state in STATES:
		if not frappe.db.exists("Workflow State", state["state"]):
			frappe.get_doc(
				{
					"doctype": "Workflow State",
					"workflow_state_name": state["state"],
					"style": "Primary",
				}
			).insert(ignore_permissions=True)
