import frappe
from frappe.utils import nowdate, date_diff

def send_password_expiry_reminders():
    # Configuration
    expiry_days = 90  # Changed from 0 to 90 for logic to make sense
    warning_days = 7
    today = nowdate()

    # Fetch accounts
    accounts = frappe.get_all(
        "Email Account", 
        fields=["name", "email_id", "custom_last_password_change"]
    )

    for acc in accounts:
        # Match field name exactly as it is in the database/DocType
        last_change = acc.get("custom_last_password_change")
        
        if last_change:
            diff = date_diff(today, last_change)
            
            # Check if today is exactly the warning day (e.g., 83 days)
            if diff == (expiry_days - warning_days):
                frappe.sendmail(
                    recipients=["naresh.dingankar@cloverinfotech.com"],
                    subject=f"Action Required: Email Password Expiry for {acc.name}",
                    message=f"The password for {acc.email_id} was last changed {diff} days ago. Please rotate it within {warning_days} days."
                )