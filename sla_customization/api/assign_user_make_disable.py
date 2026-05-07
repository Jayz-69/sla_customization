import frappe

def block_disable_with_open_tickets(doc, method=None):
    if doc.has_value_changed("enabled") and doc.enabled == 0:
        assigned_open_tickets = frappe.get_all("HD Ticket", filters={
            "custom_assigned_to": doc.name,
            "status": ["not in", ["Closed", "Resolved"]]
        })

        if assigned_open_tickets:
            links = []
            # Don't hardcode :8001; get_url() handles the correct port automatically
            base_url = frappe.utils.get_url() 
            
            for t in assigned_open_tickets:
                # Use frappe.utils.get_link_to_form for cleaner, safer links
                link = frappe.utils.get_link_to_form("HD Ticket", t.name)
                links.append(link)
            
            open_tickets_html = "<br>• " + "<br>• ".join(links)
            
            frappe.throw(
                msg=f"Cannot disable user with assigned open tickets: {open_tickets_html}",
                title="Blocking Open Tickets"
            )