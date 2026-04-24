import frappe


def delete_custom_fields(custom_fields):
    for doctypes, fields in custom_fields.items():

        if isinstance(fields, dict):
            fields = [fields]

        if isinstance(doctypes, str):
            doctypes = (doctypes,)

        for doctype in doctypes:
            frappe.db.delete(
                "Custom Field",
                {
                    "fieldname": ("in", [f["fieldname"] for f in fields]),
                    "dt": doctype,
                },
            )

            frappe.clear_cache(doctype=doctype)