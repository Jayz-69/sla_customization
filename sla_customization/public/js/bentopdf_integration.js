frappe.ui.form.on('*', {
    refresh: function(frm) {
        frm.add_custom_button(__('Download Editable Word'), function() {
            download_editable_word(frm);
        });
    }
});

function download_editable_word(frm) {
    frappe.call({
        method: 'sla_customization.api.generate_pdf_for_doc',
        args: {
            doctype: frm.doctype,
            name: frm.doc.name
        },
        freeze: true,
        freeze_message: __("Generating PDF..."),
        callback: function(r) {
            if (r.message && r.message.pdf_data) {
                frappe.show_alert({
                    message: __("Converting to DOCX..."),
                    indicator: "blue"
                });
                load_bentopdf(r.message.pdf_data, r.message.filename);
            }
        },
        error: function(r) {
            frappe.msgprint({
                title: __("Error"),
                indicator: "red",
                message: __("Failed to generate PDF. Please try again.")
            });
        }
    });
}

function load_bentopdf(pdf_data, filename) {
    const iframe = document.createElement("iframe");
    iframe.style.display = "none";
    iframe.src = "http://localhost:4173/pdf-to-docx.html";
    document.body.appendChild(iframe);

    const messageHandler = function(event) {
        if (event.origin !== "http://localhost:4173") return;

        if (event.data.type === "DOCX_READY") {
            frappe.show_alert({
                message: __("Download complete!"),
                indicator: "green"
            }, 3);
            
            const a = document.createElement("a");
            a.href = URL.createObjectURL(event.data.blob);
            a.download = event.data.filename + ".docx";
            a.click();
            document.body.removeChild(iframe);
            window.removeEventListener("message", messageHandler);
        }
    };

    window.addEventListener("message", messageHandler);

    iframe.onload = function() {
        iframe.contentWindow.postMessage({
            type: "LOAD_PDF",
            pdf_data: pdf_data,
            filename: filename
        }, "http://localhost:4173");
    };
}
