from io import BytesIO
from pathlib import Path

import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


QR_SIZE_PRESETS_MM = {
    "small": 25,
    "medium": 35,
    "large": 50,
}


def make_qr_image(url: str):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )

    qr.add_data(url)
    qr.make(fit=True)

    return qr.make_image(
        fill_color="black",
        back_color="white",
    )


def generate_label_pdf(
    *,
    asset_id: str,
    title: str,
    url: str,
    output_path: Path,
    qr_size: str = "medium",
    qr_mm: float | None = None,
) -> Path:
    if qr_mm is None:
        try:
            qr_mm = QR_SIZE_PRESETS_MM[qr_size]
        except KeyError as exc:
            raise ValueError(
                f"Unknown QR size preset: {qr_size}"
            ) from exc

    if qr_mm <= 0:
        raise ValueError("QR size must be greater than zero.")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    qr_image = make_qr_image(url)

    qr_buffer = BytesIO()
    qr_image.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)

    pdf = canvas.Canvas(
        str(output_path),
        pagesize=A4,
    )

    page_width, page_height = A4

    qr_size_points = qr_mm * mm
    qr_x = (page_width - qr_size_points) / 2
    qr_y = page_height - qr_size_points - (25 * mm)

    pdf.drawImage(
        ImageReader(qr_buffer),
        qr_x,
        qr_y,
        width=qr_size_points,
        height=qr_size_points,
        preserveAspectRatio=True,
        mask="auto",
    )

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(
        page_width / 2,
        qr_y - (10 * mm),
        asset_id,
    )

    pdf.setFont("Helvetica", 11)
    pdf.drawCentredString(
        page_width / 2,
        qr_y - (17 * mm),
        title,
    )

    pdf.setFont("Helvetica", 7)
    pdf.drawCentredString(
        page_width / 2,
        qr_y - (23 * mm),
        url,
    )

    pdf.showPage()
    pdf.save()

    return output_path