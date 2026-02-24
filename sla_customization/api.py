import frappe
from frappe.utils.pdf import get_pdf
import base64

@frappe.whitelist()
def generate_pdf_for_doc(doctype, name):
    doc = frappe.get_doc(doctype, name)
    pdf = get_pdf(frappe.get_print(doctype, name))
    pdf_base64 = base64.b64encode(pdf).decode('utf-8')
    
    return {
        "pdf_data": pdf_base64,
        "filename": name
    }
