frappe.ui.form.on('HD Ticket', {
    onload: function(frm) {
        frm.set_query("custom_assigned_to", function() {
            return {
                query: "override.api.user_query.active_user_query"
            };
        });
    }
});