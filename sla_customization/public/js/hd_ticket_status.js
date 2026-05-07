frappe.ui.form.on('HD Ticket', {
    refresh: function(frm) {
        // Checks if the ticket is closed and cancelled sets all fields to read-only
        if (frm.doc.status === 'Closed'|| frm.doc.status === 'Cancelled') {
            $.each(frm.meta.fields, function(i, field) {
                frm.set_df_property(field.fieldname, 'read_only', 1);
            });
        }
    }
});
