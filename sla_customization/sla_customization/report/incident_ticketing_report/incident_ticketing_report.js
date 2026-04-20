// Copyright (c) 2026, Jay Anjarlekar and contributors
// For license information, please see license.txt

frappe.query_reports["Incident Ticketing Report"] = {
        "filters": [
        {
            "fieldname": "territories",
            "label": __("Territories"),
            "fieldtype": "MultiSelect",
            "options" : []
        },
        {
            "fieldname": "customer_group",
            "label": __("Customer Group"),
            "fieldtype": "MultiSelect",
            "options": ["Individual", "Commercial", "Non Profit"] // Static example
        }
    ],
    "onload": function(report) {
        // Fetch the data manually
        console.log("in onload")
        frappe.db.get_list('Email Account', { pluck: 'name' }).then(data => {
            // Get the filter object
            let f = report.get_filter('territories');
            console.log(data,f)
            // Set the options and refresh the control
            f.set_data(data); 
            f.refresh();
        });
    }
};
