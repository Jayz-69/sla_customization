CUSTOM_FIELDS = {

    "HD Ticket": [

        {
            "fieldname": "custom_entry_type",
            "label": "Entry Type",
            "fieldtype": "Link",
            "options": "Ticket",
            "insert_after": "subject_section",
            "default": "Incident"
        },
        
        {
            "fieldname": "custom_sr_category_copy",
            "label": "SR Category",
            "fieldtype": "Select",
            "options": "Oracle-DB Administration/Oracle-Scheduling jobs\nOracle-DB Administration/Oracle-Creating Jobs/Triggers/scripts\nOracle-DB Administration/Oracle-Defragmentation/Shrink Database\nOracle-DB Administration/Oracle-Table stats gathering\nOracle-DB Administration/Oracle-Index Optimization\nOracle-DB Administration/Oracle-DB Creation\nOracle-DB Administration/Oracle-Oracle Binaries installation and Configuration\nOracle-DB Administration/Oracle-Oracle Client Installation and configuration\nOracle-DB Administration/Oracle-Oracle DB upgrades\nOracle-DB Administration/Oracle-Oracle DB Migration\nOracle-DB Administration/Oracle-user creation and Management\nOracle-DB Administration/Oracle-DR/Standby Planning and implementation\nOracle-DB Administration/Oracle-DB Sanity/integrity check\nOracle-DB Administration/Oracle-Updating DB Inventory\nOracle-DB Administration/Oracle-DB Links management\nOracle-DB Administration/Oracle-Configuring email Alerts\nOracle-DB Backup Recovery/Oracle-Backups-RMAN/Datapump/Exp-Imp\nOracle-DB Backup Recovery/Oracle-Data Recovery Testing/Restoration Drill\nOracle-DB Backup Recovery/Oracle-Archive log backups\nOracle-DB Backup Recovery/Oracle-Schema Refresh\nOracle-DB Backup Recovery/Oracle-Table refresh\nOracle-DB Backup Recovery/Oracle-DB Cloning/refresh\nOracle-DB Backup Recovery/Oracle-Datafile restoration\nOracle-DB Performance Tuning/Oracle-DB Optimization\nOracle-DB Performance Tuning/Oracle-Performance Tuning\nOracle-DB Performance Tuning/Oracle-AWR/ADDM/ASH analysis\nOracle-DB Performance Tuning/Oracle-Disk Space Monitoring\nOracle-DB Performance Tuning/Oracle-Capacity planning\nOracle-DB Security/Oracle-DB Hardening\nOracle-DB Security/Oracle-VAPT Reports\nOracle-DB Security/Oracle-Patch management\nOracle-DB Security/Oracle-DB Encryption configuration\nOracle-DB Reporting/Oracle-Monitoring Alerts/Logs/Sync/\nOracle-DB Reporting/Oracle-Daily Monitoring reports\nOracle-DB-Others/Oracle-Others\nMySQL-DB Administration/MySQL-DB Sanity/integrity check\nMySQL-DB Administration/MySQL-Updating DB Inventory\nMySQL-DB Administration/MySQL-Database Creation\nMySQL-DB Administration/MySQL-DB Upgrades - Minor\nMySQL-DB Administration/MySQL-User Management\nMySQL-DB Administration/MySQL-Deployments\nMySQL-DB Administration/MySQL-Installation and Configuration - Repo/Packages, Tarball\nMySQL-DB Administration/MySQL-DB Migration\nMySQL-DB Administration/MySQL-Scheduling jobs\nMySQL-DB Administration/MySQL-Database maintenance activity\nMySQL-DB Administration/MySQL-Creating Jobs/Triggers/scripts\nMySQL-DB Administration/MySQL-Defragmentation\nMySQL-DB Administration/MySQL-Index Optimization",
            "insert_after": "custom_sr_category"
        },

        {
            "fieldname": "custom_column_break_z01jm",
            "fieldtype": "Column Break",
            "insert_after": "subject_section"
        },
        {
            "fieldname": "custom_column_break_uupc9",
            "fieldtype": "Column Break",
            "insert_after": "additional_info"
        },
        {
            "fieldname": "custom_column_break_gkel5",
            "fieldtype": "Column Break",
            "insert_after": "custom_cancellation_remarks"
        },
        {
            "fieldname": "custom_column_break_vtgdn",
            "fieldtype": "Column Break",
            "insert_after": "custom_schedule_date"
        },
        {
            "fieldname": "custom_section_break_nrigx",
            "fieldtype": "Section Break",
            "insert_after": "custom_service_window"
        },
        {
            "fieldname": "custom_section_break_4nvqt",
            "label": "Assignments",
            "fieldtype": "Section Break",
            "insert_after": "contact"
        },
        {
            "fieldname": "custom_tab_9",
            "label": "Communication",
            "fieldtype": "Tab Break",
            "insert_after": "custom_etr_history"
        },
        {
            "fieldname": "custom_etr",
            "label": "ETR",
            "fieldtype": "Tab Break",
            "insert_after": "key"
        },
        {
            "fieldname": "custom_expected_time",
            "label": "Expected Time",
            "fieldtype": "Datetime",
            "insert_after": "custom_etr"
        },
        {
            "fieldname": "custom_etr_justification",
            "label": "ETR Justification",
            "fieldtype": "Data",
            "insert_after": "custom_expected_time"
        },
        {
            "fieldname": "custom_etr_history",
            "label": "ETR History",
            "fieldtype": "Table",
            "options": "ETR History",
            "insert_after": "custom_etr_justification"
        },
        {
            "fieldname": "custom_actual_effortss",
            "label": "Actual Efforts",
            "fieldtype": "Duration",
            "insert_after": "custom_tab_9"
        },
        {
            "fieldname": "custom_resolution_sla_breach",
            "label": "Resolution SLA Breach",
            "fieldtype": "Select",
            "options": "NO\nYES",
            "insert_after": "total_hold_time"
        },
        {
            "fieldname": "custom_response_sla_breach",
            "label": "Response SLA Breach",
            "fieldtype": "Select",
            "options": "NO\nYES",
            "insert_after": "response_by"
        },
        {
            "fieldname": "custom_solution",
            "label": "Solution",
            "fieldtype": "Small Text",
            "insert_after": "custom_resolution_code"
        },
        {
            "fieldname": "custom_resolution_code",
            "label": "Resolution Code",
            "fieldtype": "Select",
            "options": "SELECT\nResolved",
            "insert_after": "custom_pending_reason"
        },
        {
            "fieldname": "custom_pending_reason",
            "label": "Pending Reason",
            "fieldtype": "Select",
            "options": "Pending from Client\nPending from Partner\nOthers",
            "insert_after": "custom_column_break_gkel5"
        },
        {
            "fieldname": "custom_closure_category",
            "label": "Closure Category",
            "fieldtype": "Select",
            "options": "UAM\nProd Issue\nAudit",
            "insert_after": "custom_closure_code"
        },
        {
            "fieldname": "custom_closure_code",
            "label": "Closure Code",
            "fieldtype": "Select",
            "options": "Closed\nResolved\nOthers",
            "insert_after": "custom_section_break_nrigx"
        },
        {
            "fieldname": "custom_service_window",
            "label": "Service Window",
            "fieldtype": "Select",
            "options": "24*7\n9*6\n16*6",
            "insert_after": "custom_assigned_to"
        },
        {
            "fieldname": "custom_schedule_date",
            "label": "Schedule Date",
            "fieldtype": "Datetime",
            "insert_after": "agent_group"
        },
        {
            "fieldname": "custom_priorityy",
            "label": "Priority",
            "fieldtype": "Select",
            "options": "P1\nP2\nP3\nP4",
            "insert_after": "custom_impact",
            "default": "P3"
        },
        {
            "fieldname": "custom_impact",
            "label": "Impact",
            "fieldtype": "Select",
            "options": "Severity 1\nSeverity 2\nSeverity 3\nSeverity 4",
            "insert_after": "priority",
            "default": "Severity 3"
        },
        {
            "fieldname": "custom_sr_classification_copy",
            "label": "SR Classification",
            "fieldtype": "Select",
            "options": "Administration\nDatabase / Power BI\nDatabase / Oracle Cloud - OS\nDatabase / Oracle Cloud - Database\nDatabase / Oracle Cloud - Network\nBackup\nPerformance Testing\nDisaster Recovery/Replication\nAudit/Hardening\nReporting\nSecurity\nEncryption\nUpgrade\nMigration\nNetwork Services",
            "insert_after": "ticket_type"
        },

        {
            "fieldname": "custom_reason_for_change",
            "label": "Reason For Change",
            "fieldtype": "Data",
            "insert_after": "custom_priorityy"
        },
        {
            "fieldname": "custom_sr_category",
            "label": "SR Category",
            "fieldtype": "Link",
            "options": "Classification",
            "insert_after": "custom_classification_category"
        },
        {
            "fieldname": "custom_assigned_to",
            "label": "Assigned To",
            "fieldtype": "Link",
            "options": "User",
            "insert_after": "custom_column_break_vtgdn"
        },
        {
            "fieldname": "custom_demo",
            "label": "Demo",
            "fieldtype": "Data",
            "insert_after": "custom_related_configuration_items"
        },
        {
            "fieldname": "custom_related_configuration_items",
            "label": "Related Configuration Items",
            "fieldtype": "Data",
            "insert_after": "custom_related_change_records"
        },
        {
            "fieldname": "custom_related_change_records",
            "label": "Related Change Records",
            "fieldtype": "Data",
            "insert_after": "custom_possible_root_causes"
        },
        {
            "fieldname": "custom_possible_root_causes",
            "label": "Possible Root Causes",
            "fieldtype": "Data",
            "insert_after": "custom_data"
        },
        {
            "fieldname": "custom_data",
            "label": "Possible Remediations",
            "fieldtype": "Data",
            "insert_after": "custom_similar_closedresolved_incidents"
        },
        {
            "fieldname": "custom_similar_closedresolved_incidents",
            "label": "Similar Closed/Resolved Incidents",
            "fieldtype": "Data",
            "insert_after": "custom_similar_open_incidents"
        },
        {
            "fieldname": "custom_similar_open_incidents",
            "label": "Similar Open Incidents",
            "fieldtype": "Data",
            "insert_after": "custom_troubleshoot"
        },
        {
            "fieldname": "custom_troubleshoot",
            "label": "Troubleshoot",
            "fieldtype": "Section Break",
            "insert_after": "custom_tab_8"
        },
        {
            "fieldname": "custom_tab_8",
            "label": "Troubleshoot",
            "fieldtype": "Tab Break",
            "insert_after": "amended_from"
        },
        {
            "fieldname": "custom_cancel_edit_used",
            "label": "Cancel Edit Used",
            "fieldtype": "Check",
            "insert_after": "subject"
        },
        {
            "fieldname": "custom_reason_for_change__entry_type",
            "label": "Reason For Change - Entry Type",
            "fieldtype": "Data",
            "insert_after": "custom_entry_type"
        },
        {
            "fieldname": "custom_is_incident_conversion",
            "label": "Is Incident Conversion",
            "fieldtype": "Check",
            "insert_after": "workflow_state"
        },
        {
            "fieldname": "custom_sr_id",
            "label": "SR ID",
            "fieldtype": "Link",
            "options": "HD Ticket",
            "insert_after": "custom_is_incident_conversion"
        },
        {
            "fieldname": "custom_workgroup",
            "label": "Workgroup",
            "fieldtype": "Link",
            "options": "HD Team",
            "insert_after": "email_account"
        },
        {
            "fieldname": "custom_logged_time",
            "label": "Logged Time",
            "fieldtype": "Datetime",
            "insert_after": "summary"
        },

        {
            "fieldname": "workflow_state",
            "label": "Workflow State",
            "fieldtype": "Link",
            "options": "Workflow State"
        },

        {
            "fieldname": "custom_resolution_sla_failure_reason", 
            "label": "Resolution SLA Failure Reason", 
            "fieldtype": "Data",
            "insert_after": "custom_resolution_sla_breach",
            "depends_on": 'eval:doc.custom_resolution_sla_breach == "YES"',
            "mandatory_depends_on": 'eval:doc.custom_resolution_sla_breach == "YES"'
        },
        {
            "fieldname": "custom_response_sla_failure_reason", 
            "label": "Response SLA Failure Reason", 
            "fieldtype": "Data",
            "insert_after": "custom_response_sla_breach",
            "depends_on": 'eval:doc.custom_response_sla_breach == "YES"',
            "mandatory_depends_on": 'eval:doc.custom_response_sla_breach == "YES"'
        },

        {
            "fieldname": "custom_cancellation_remarks",
            "label": "Cancellation Remarks",
            "fieldtype": "Data",
            "options": "HD Team",
            "insert_after": "custom_closure_category"
        },

        {
            "fieldname": "custom_cancellation_remarks", 
            "label": "Cancellation Remarks", 
            "fieldtype": "Data",
            "insert_after": "custom_closure_category",
            "depends_on": 'eval:!["New","In-Progress"].includes(doc.status)'
        },

        {
            "fieldname": "custom_classification_category", 
            "label": "Category", 
            "fieldtype": "Select",
            "options": "Database\nMiddleware\nIncident",
            "insert_after": "custom_sr_classification_copy",
            "depends_on": 'eval:doc.custom_entry_type == "Incident"',
            "mandatory_depends_on": 'eval:doc.custom_entry_type == "Incident"'
        },
    ],


    "Email Account": [

        {
            "fieldname": "custom_last_password_change",
            "label": "Last Password Change",
            "fieldtype": "Date",
            "insert_after": "ascii_encode_password"
        },
        {
            "fieldname": "custom_parent_email",
            "label": "Parent Email",
            "fieldtype": "Data",
            "insert_after": "custom_workgroup"
        },
        {
            "fieldname": "custom_workgroup",
            "label": "Workgroup",
            "fieldtype": "Link",
            "options": "HD Team",
            "insert_after": "frappe_mail_site"
        },

         {
            "fieldname": "custom_workgroup_owner",
            "label": "Workgroup Owner",
            "fieldtype": "Link",
            "options": "User",
            "insert_after": "frappe_mail_site"
        }
    ]

}