import io
from flask import Blueprint
from PIL import Image
from rembg import remove

from utils.decorators import process_image_request
from utils.helpers import safe_gc_collect, send_file_and_cleanup

remove_bp = Blueprint("removebg", __name__)


@remove_bp.route("/removeBg", methods=["POST"])
@process_image_request
def remove_bg(img, filename, file_bytes):
    base = filename.rsplit('.', 1)[0]

    # Run background removal using the uploaded file bytes
    output_bytes = remove(file_bytes)

    out_img = None
    try:
        out_img = Image.open(io.BytesIO(output_bytes))

        # Save processed image to memory buffer
        buf = io.BytesIO()
        out_img.save(buf, format="PNG", optimize=True)
        buf.seek(0)
        data = buf.getvalue()
    finally:
        if out_img:
            try:
                out_img.close()
            except Exception:
                pass
            out_img = None

        try:
            del output_bytes
            safe_gc_collect()
        except Exception:
            pass

    return send_file_and_cleanup(
        data,
        mimetype="image/png",
        as_attachment=True,
        download_name=f"{base}_no_bg.png",
        max_age=0,
    )
