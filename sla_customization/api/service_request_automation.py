# import frappe

# def run_oracle_rds_jobs():
#     jobs = ["#ABSLAMC--  Send morning monitoring report","#INDIAN HOTEL--  Send morning monitoring report","#TVS--  Send morning monitoring report"]
#     for data in jobs:
#         doc = frappe.new_doc("Services Request")
#         doc.custom_subject = data
#         doc.custom_classification = "Reporting"
#         doc.custom_team = "OFFSITE ORACLERDS SUPPORT"
#         doc.save()
#     frappe.db.commit() 
