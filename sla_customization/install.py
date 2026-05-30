import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from sla_customization.setup.property_setters import create_property_setters
from sla_customization.constants.custom_fields import CUSTOM_FIELDS
from sla_customization.setup.change_record_workflow import setup_change_record_workflow


def after_install():

    create_custom_fields(CUSTOM_FIELDS, ignore_validate=True)
    create_property_setters()
    setup_change_record_workflow()