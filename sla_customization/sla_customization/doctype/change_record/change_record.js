// Copyright (c) 2026, Jay Anjarlekar and contributors
// For license information, please see license.txt

frappe.ui.form.on("Change Record", {
	refresh(frm) {
		fetch_workgroup_owner_details(frm);
	},

	owner_workgroup(frm) {
		if (frm.doc.owner_workgroup && !frm.doc.assigned_workgroup) {
			frm.set_value("assigned_workgroup", frm.doc.owner_workgroup);
		}
		fetch_workgroup_owner_details(frm);
	},
});

function fetch_workgroup_owner_details(frm) {
	if (!frm.doc.owner_workgroup) {
		frm.set_value("workgroup_owner_details", "");
		return;
	}

	frappe.call({
		method: "sla_customization.sla_customization.doctype.change_record.change_record.get_workgroup_owner_details",
		args: {
			team: frm.doc.owner_workgroup,
		},
		callback(r) {
			if (r.message !== undefined) {
				frm.set_value("workgroup_owner_details", r.message);
			}
		},
	});
}
