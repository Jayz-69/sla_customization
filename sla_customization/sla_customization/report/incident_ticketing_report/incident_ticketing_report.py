# Copyright (c) 2026, Jay Anjarlekar and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters: dict | None = None):
	"""Return columns and data for the report.

	This is the main entry point for the report. It accepts the filters as a
	dictionary and should return columns and data. It is called by the framework
	every time the report is refreshed or a filter is updated.
	"""
	columns = get_columns()
	data = get_data(filters)

	return columns, data


def get_columns() -> list[dict]:
	"""Return columns for the report.

	One field definition per column, just like a DocType field definition.
	"""
	return [
		{
			"label": _("From Date"),
			"fieldname": "from_date",
			"fieldtype": "Date",
		},
		{
			"label": _("To Date"),
			"fieldname": "to_date",
			"fieldtype": "Date",
		},

	]


def get_data(filters) -> list[list]:
	if filter:
		frappe.log_error(filters)
	return [
		["Row 1", 1],
		["Row 2", 2],
	]
