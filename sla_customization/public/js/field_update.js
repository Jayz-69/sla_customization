frappe.ui.form.on('HD Ticket', {
    
    refresh: function(frm) {

        // SUBJECT READ ONLY IF EMAIL CREATED
        if (frm.doc.via_customer_portal == 0 && frm.doc.email_account) {
            frm.set_df_property('subject', 'read_only', 1);
        } else {
            frm.set_df_property('subject', 'read_only', 0);
        }

        // BLOCK DUPLICATE IF SLA BREACH REASON NOT FILLED
        intercept_duplicate_for_sla_breach(frm);

        toggle_fields(frm);
    },

    status: function(frm) {
        toggle_fields(frm);
    }

});

function toggle_fields(frm) {
    if (frm.doc.status === "New") {
        frm.set_df_property('custom_cancellation_remarks', 'hidden', 0);
        frm.set_df_property('custom_cancellation_remarks', 'read_only', 0);
        frm.set_df_property('custom_pending_reason', 'hidden', 1);
        frm.set_df_property('custom_closure_code', 'hidden', 1);
        frm.set_df_property('custom_closure_category', 'hidden', 1);
        frm.set_df_property('custom_resolution_code', 'hidden', 1);
        frm.set_df_property('custom_solution', 'hidden', 1);
        frm.refresh_fields(['custom_pending_reason','custom_closure_code','custom_closure_category','custom_resolution_code','custom_solution','custom_cancellation_remarks']);
    }
    if (frm.doc.status === "Pending") {
        frm.set_df_property('custom_pending_reason', 'hidden', 0);
        frm.set_df_property('custom_pending_reason', 'read_only', 1);
        frm.set_df_property('custom_cancellation_remarks', 'hidden', 1);
        frm.set_df_property('custom_closure_code', 'hidden', 1);
        frm.set_df_property('custom_closure_category', 'hidden', 1);
        frm.set_df_property('custom_resolution_code', 'hidden', 1);
        frm.set_df_property('custom_solution', 'hidden', 1);
        frm.refresh_fields(['custom_pending_reason','custom_cancellation_remarks','custom_closure_code','custom_closure_category','custom_resolution_code','custom_solution']);
    }
    if (frm.doc.status === "In-Progress") {
        frm.set_df_property('custom_pending_reason', 'hidden', 0);
        frm.set_df_property('custom_pending_reason', 'read_only', 0);
        frm.set_df_property('custom_cancellation_remarks', 'hidden', 0);
        frm.set_df_property('custom_cancellation_remarks', 'read_only', 0);
        frm.set_df_property('custom_resolution_code', 'hidden', 0);
        frm.set_df_property('custom_resolution_code', 'read_only', 0);
        frm.set_df_property('custom_solution', 'hidden', 0);
        frm.set_df_property('custom_solution', 'read_only', 0);
        frm.set_df_property('custom_closure_code', 'hidden', 1);
        frm.set_df_property('custom_closure_category', 'hidden', 1);
        frm.refresh_fields(['custom_pending_reason','custom_cancellation_remarks','custom_resolution_code','custom_solution','custom_closure_code','custom_closure_category']);
    }
    if (frm.doc.status === "Resolved") {
        frm.set_df_property('custom_closure_code', 'hidden', 0);
        frm.set_df_property('custom_closure_code', 'read_only', 0);
        frm.set_df_property('custom_closure_category', 'hidden', 0);
        frm.set_df_property('custom_closure_category', 'read_only', 0);
        frm.set_df_property('custom_pending_reason', 'hidden', 1);
        frm.set_df_property('custom_cancellation_remarks', 'hidden', 1);
        frm.set_df_property('custom_resolution_code', 'hidden', 1);
        frm.set_df_property('custom_solution', 'hidden', 1);
        frm.refresh_fields(['custom_pending_reason','custom_cancellation_remarks','custom_resolution_code','custom_solution','custom_closure_code','custom_closure_category']);
    }
    if (frm.doc.status === "Cancelled") {
        frappe.ui.form.on('HD Ticket', {
 
    onload_post_render: function(frm) {
 
        setTimeout(() => {
 
            // Detect duplicate (SR → Incident)
            let is_duplicate = frm.is_new() && frm.doc.__unsaved && frm.doc.subject;
 
            // Show/Hide fields
            frm.toggle_display("custom_is_incident_conversion", is_duplicate);
            frm.toggle_display("custom_sr_id", is_duplicate);
 
            if (is_duplicate) {
 
                // Auto check
                frm.set_value("custom_is_incident_conversion", 1);
 
                // Set Entry Type
                frm.set_value("custom_entry_type", "Incident");
 
                // Reset Logged Time to current
                frm.set_value("custom_logged_time", frappe.datetime.now_datetime());

                // Reset SLA breach fields — should not carry over from SR to Incident
                frm.set_value("custom_response_sla_breach", "NO");
                frm.set_value("custom_resolution_sla_breach", "NO");
                frm.set_value("custom_response_sla_failure_reason", "");
                frm.set_value("custom_resolution_sla_failure_reason", "");
 
            }
 
        }, 300);
    }
 
});frm.set_df_property('custom_cancellation_remarks', 'hidden', 0);
        frm.set_df_property('custom_cancellation_remarks', 'read_only', 1);
        frm.set_df_property('custom_pending_reason', 'hidden', 1);
        frm.set_df_property('custom_closure_code', 'hidden', 1);
        frm.set_df_property('custom_closure_category', 'hidden', 1);
        frm.set_df_property('custom_resolution_code', 'hidden', 1);
        frm.set_df_property('custom_solution', 'hidden', 1);
        frm.refresh_fields(['custom_pending_reason','custom_closure_code','custom_closure_category','custom_resolution_code','custom_solution','custom_cancellation_remarks']);
    }
}

function intercept_duplicate_for_sla_breach(frm) {
    if (frm.is_new() || frm.doc.custom_entry_type !== "Service Request" || frm.doc.custom_is_incident_conversion) return;

    // Timeout ensures the framework finishes rendering the page action menu options completely
    setTimeout(() => {
        let duplicate_btn = frm.page.menu.find('a:contains("Duplicate")');

        if (duplicate_btn.length) {
            // Unbind Frappe's native redirect trigger completely so we can control it
            duplicate_btn.off("click").on("click", function(e) {
                
                const response_breached = frm.doc.custom_response_sla_breach === "YES";
                const resolution_breached = frm.doc.custom_resolution_sla_breach === "YES";
                
                let missing = [];

                if (response_breached && !frm.doc.custom_response_sla_failure_reason) {
                    missing.push("<b>Response SLA Failure Reason</b>");
                }
                if (resolution_breached && !frm.doc.custom_resolution_sla_failure_reason) {
                    missing.push("<b>Resolution SLA Failure Reason</b>");
                }

                // CASE 1: Validation fails, prevent duplication
                if (missing.length) {
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();

                    frappe.msgprint({
                        title: __("Cannot Duplicate — SLA Breach"),
                        message: __("Please fill the following field(s) on this Service Request before creating an Incident:<br><br>") + missing.join("<br>"),
                        indicator: "red"
                    });
                    return false;
                }

                // CASE 2: Validation passes! Manually execute Frappe's native clone script
                frappe.model.with_doctype(frm.doctype, function() {
                    let new_doc = frappe.model.copy_doc(frm.doc);
                    frappe.set_route("Form", frm.doctype, new_doc.name);
                });
            });
        }
    }, 500);
}