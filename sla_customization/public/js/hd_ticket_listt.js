// your_custom_app/public/js/hd_ticket_list_override.js

frappe.listview_settings['HD Ticket'] = {
    onload: function(listview) {
        console.log("Custom Override Active for HD Ticket");
    },

    add_fields: ["response_by", "resolution_by", "status"],

    formatters: {
        response_by: function(val, df, doc) {
            return custom_format_with_dot(val, doc, "Response");
        },
        resolution_by: function(val, df, doc) {
            return custom_format_with_dot(val, doc, "Resolution");
        }
    }
};

function custom_format_with_dot(val, doc, type) {
    if (!val) return "";

    const now = frappe.datetime.now_datetime();
    let dot_color = "green"; 
    
    if (doc.status !== "Closed") {
        let diff_in_hours = frappe.datetime.get_diff(val, now) * 24;

        if (val < now) {
            dot_color = "red";
        } else if (diff_in_hours <= 2) {
            dot_color = "orange"; // Changed yellow to orange for better visibility
        }
    } else {
        dot_color = "gray";
    }

    const formatted_date = frappe.datetime.str_to_user(val);
    
    return `
        <span style="display: flex; align-items: center;">
            <span class="indicator ${dot_color}" 
                  style="margin-right: 8px;"></span>
            <span>${formatted_date}</span>
        </span>
    `;
}
