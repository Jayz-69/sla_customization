frappe.ui.form.on('HD Ticket', {
    
    refresh: function(frm) {
 
        // =========================
        // SUBJECT READ ONLY IF EMAIL CREATED
        // =========================
        if (frm.doc.via_customer_portal == 0 && frm.doc.email_account) {
            frm.set_df_property('subject', 'read_only', 1);
        } else {
            frm.set_df_property('subject', 'read_only', 0);
        }
 
        toggle_fields(frm);
    },
 
    status: function(frm) {
        toggle_fields(frm);
    }
 
});
 
function toggle_fields(frm) {
 
    // =========================
    // NEW
    // =========================
    if (frm.doc.status === "New") {
 
        frm.set_df_property('custom_cancellation_remarks', 'hidden', 0);
        frm.set_df_property('custom_cancellation_remarks', 'read_only', 0);
 
        frm.set_df_property('custom_pending_reason', 'hidden', 1);
        frm.set_df_property('custom_closure_code', 'hidden', 1);
        frm.set_df_property('custom_closure_category', 'hidden', 1);
        frm.set_df_property('custom_resolution_code', 'hidden', 1);
        frm.set_df_property('custom_solution', 'hidden', 1);
 
        frm.refresh_fields([
            'custom_pending_reason',
            'custom_closure_code',
            'custom_closure_category',
            'custom_resolution_code',
            'custom_solution',
            'custom_cancellation_remarks'
        ]);
    }
 
    // =========================
    // PENDING
    // =========================
    if (frm.doc.status === "Pending") {
 
        frm.set_df_property('custom_pending_reason', 'hidden', 0);
        frm.set_df_property('custom_pending_reason', 'read_only', 1);
 
        frm.set_df_property('custom_cancellation_remarks', 'hidden', 1);
        frm.set_df_property('custom_closure_code', 'hidden', 1);
        frm.set_df_property('custom_closure_category', 'hidden', 1);
        frm.set_df_property('custom_resolution_code', 'hidden', 1);
        frm.set_df_property('custom_solution', 'hidden', 1);
 
        frm.refresh_fields([
            'custom_pending_reason',
            'custom_cancellation_remarks',
            'custom_closure_code',
            'custom_closure_category',
            'custom_resolution_code',
            'custom_solution'
        ]);
    }
 
    // =========================
    // IN-PROGRESS
    // =========================
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
 
        frm.refresh_fields([
            'custom_pending_reason',
            'custom_cancellation_remarks',
            'custom_resolution_code',
            'custom_solution',
            'custom_closure_code',
            'custom_closure_category'
        ]);
    }
 
    // =========================
    // RESOLVED
    // =========================
    if (frm.doc.status === "Resolved") {
 
        frm.set_df_property('custom_closure_code', 'hidden', 0);
        frm.set_df_property('custom_closure_code', 'read_only', 0);
 
        frm.set_df_property('custom_closure_category', 'hidden', 0);
        frm.set_df_property('custom_closure_category', 'read_only', 0);
 
        frm.set_df_property('custom_pending_reason', 'hidden', 1);
        frm.set_df_property('custom_cancellation_remarks', 'hidden', 1);
        frm.set_df_property('custom_resolution_code', 'hidden', 1);
        frm.set_df_property('custom_solution', 'hidden', 1);
 
        frm.refresh_fields([
            'custom_pending_reason',
            'custom_cancellation_remarks',
            'custom_resolution_code',
            'custom_solution',
            'custom_closure_code',
            'custom_closure_category'
        ]);
    }
 
    // =========================
    // CANCELLED
    // =========================
    if (frm.doc.status === "Cancelled") {
 
        frm.set_df_property('custom_cancellation_remarks', 'hidden', 0);
        frm.set_df_property('custom_cancellation_remarks', 'read_only', 1);
 
        frm.set_df_property('custom_pending_reason', 'hidden', 1);
        frm.set_df_property('custom_closure_code', 'hidden', 1);
        frm.set_df_property('custom_closure_category', 'hidden', 1);
        frm.set_df_property('custom_resolution_code', 'hidden', 1);
        frm.set_df_property('custom_solution', 'hidden', 1);
 
        frm.refresh_fields([
            'custom_pending_reason',
            'custom_closure_code',
            'custom_closure_category',
            'custom_resolution_code',
            'custom_solution',
            'custom_cancellation_remarks'
        ]);
    }
 
}
 
