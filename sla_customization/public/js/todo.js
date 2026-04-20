frappe.ui.form.on('HD Ticket', {
    onload: function(frm) {
	console.log("onload2 called")
        frm.set_query("custom_assigned_to", function() {
            return {
                query: "sla_customization.api.user_query.active_user_query",
                filters: {
                    "email_account": frm.doc.email_account
                }
            };
        });
     },
   custom_assigned_to:function(frm) {
         console.log("custom_assigned called")
	 frm.set_query("custom_assigned_to", function() {
    
       return {
                query: "sla_customization.api.user_query.active_user_query",
                filters: {
                    "email_account": frm.doc.email_account 
                }

            };
        });
    }
//    refresh: function(frm) {
//       console.log("refresh called")
//  	 // Find the input element of your custom field
//         frm.fields_dict['custom_assigned_to'].$input.on('click', function() {
            
// 	    console.log("inside refresh custom field")
// 		// Re-register the query every time the field is clicked
//             frm.set_query("custom_assigned_to", function() {
//                 console.log("API query triggered via click");
//                return {
//                     query: "sla_customization.api.user_query.active_user_query"
//                 };
//             });
//         });
//     }
});
