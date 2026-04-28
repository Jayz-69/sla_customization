from email import message_from_string
 
import frappe
from frappe import _
from frappe.email.doctype.email_account.email_account import EmailAccount
from frappe.email.receive import InboundMail
 
 
class CustomEmailAccount(EmailAccount):
 
    def get_inbound_mails(self) -> list[InboundMail]:
        """Retrieve and return inbound mails."""
        mails = []
 
        def process_mail(messages, append_to=None):
            for index, message in enumerate(messages.get("latest_messages", [])):
                try:
                    _msg = message_from_string(
                        message.decode("utf-8", errors="replace")
                    )
 
                    # 🔥 Skip auto-generated emails
                    if _msg.get("X-Auto-Generated"):
                        continue
 
                    # 🔥 Detect reply emails
                    is_reply = _msg.get("In-Reply-To") or _msg.get("References")
 
                    # 👉 If reply → attach to existing HD Ticket
                    if is_reply:
                        append_to = "HD Ticket"
 
                    uid = (
                        messages["uid_list"][index]
                        if messages.get("uid_list")
                        else None
                    )
 
                    seen_status = messages.get("seen_status", {}).get(uid)
 
                    if self.email_sync_option != "UNSEEN" or seen_status != "SEEN":
 
                        _inbound_mail = InboundMail(
                            message,
                            self,
                            frappe.safe_decode(uid),
                            seen_status,
                            append_to,
                        )
 
                        mails.append(_inbound_mail)
 
                except Exception as e:
                    # Log error but continue
                    frappe.log_error(
                        title=_(
                            "Error processing email at index {0}, message: {1}"
                        ).format(index, e),
                        message=frappe.get_traceback(),
                    )
 
                    self.handle_bad_emails(index, message, frappe.get_traceback())
                    continue
 
        # 🔹 Incoming disabled
        if not self.enable_incoming:
            return []
 
        try:
            if self.service == "Frappe Mail":
                frappe_mail_client = self.get_frappe_mail_client()
                messages = frappe_mail_client.pull_raw(
                    last_synced_at=self.last_synced_at
                )
 
                process_mail(messages)
 
                self.db_set(
                    "last_synced_at",
                    messages["last_synced_at"],
                    update_modified=False,
                )
 
            else:
                email_sync_rule = self.build_email_sync_rule()
 
                frappe.log_error(
                    email_sync_rule + f' TO "{self.custom_parent_email}" SLA Cusomization app'
                )
 
                email_server = self.get_incoming_server(
                    in_receive=True,
                    email_sync_rule=email_sync_rule + f' TO "{self.custom_parent_email}"',
                )
 
                if self.use_imap:
                    for folder in self.imap_folder:
                        if email_server.select_imap_folder(folder.folder_name):
 
                            email_server.settings["uid_validity"] = folder.uidvalidity
 
                            messages = (
                                email_server.get_messages(
                                    folder=f'"{folder.folder_name}"'
                                )
                                or {}
                            )
 
                            process_mail(messages, folder.append_to)
 
                else:
                    messages = email_server.get_messages() or {}
                    process_mail(messages)
 
                email_server.logout()
 
        except Exception:
            self.log_error(
                title=_(
                    "Error while connecting to email account {0}"
                ).format(self.name)
            )
            return []
 
        return mails
