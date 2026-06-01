import fitz
import io
from flask import Blueprint, request
from utils.helpers import error, send_file_and_cleanup
from utils.validators import validate_uploaded_file, validate_pdf_file

sign_bp = Blueprint("sign", __name__)


@sign_bp.route("/sign/signPdf", methods=["POST"])
def sign_pdf():
    try:
        pdf_file, filename, upload_error = validate_uploaded_file(request, "file")
        if upload_error:
            return upload_error

        pdf_error = validate_pdf_file(filename)
        if pdf_error:
            return pdf_error

        signature_text = request.form.get("signature", "").strip()
        if not signature_text:
            return error("Signature text is required", 400)

        pdf_bytes = pdf_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        # Stamp signature text on the last page, bottom-right
        page = doc[-1]
        rect = fitz.Rect(
            page.rect.width - 220,
            page.rect.height - 60,
            page.rect.width - 20,
            page.rect.height - 20
        )
        page.insert_textbox(rect, signature_text, fontsize=14, color=(0, 0, 0.6))

        out = io.BytesIO()
        doc.save(out)
        doc.close()
        out.seek(0)

        return send_file_and_cleanup(
            out.getvalue(),
            mimetype="application/pdf",
            as_attachment=True,
            download_name="signed.pdf",
        )
    except Exception as e:
        return error(str(e), 500)
