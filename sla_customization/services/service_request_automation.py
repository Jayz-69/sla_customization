import frappe

def create_service_requests(*args):
    frappe.log_error(title = "sr_error",message = str(args))
