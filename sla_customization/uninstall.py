import frappe

from sla_customization.constants.custom_fields import CUSTOM_FIELDS
from sla_customization.setup.property_setters import get_property_setters
from sla_customization.utils.custom_fields import delete_custom_fields


def before_uninstall():
    delete_custom_fields(CUSTOM_FIELDS)
    delete_property_setters()


def delete_property_setters():
    field_map = {
        "doctype": "doc_type",
        "fieldname": "field_name",
    }

    for ps in get_property_setters():
        ps_copy = ps.copy()

        for key, db_field in field_map.items():
            if key in ps_copy:
                ps_copy[db_field] = ps_copy.pop(key)

        ps_copy.pop("property_type", None)
        ps_copy.pop("value", None)

        frappe.db.delete("Property Setter", ps_copy)

        frappe.clear_cache(doctype=ps.get("doctype"))