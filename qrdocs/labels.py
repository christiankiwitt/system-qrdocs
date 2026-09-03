from io import BytesIO
from pathlib import Path

import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


QR_SIZE_PRESETS_MM = {
    "tiny": 10,
    "small": 25,
    "medium": 35,
    "large": 50,
}

PAGE_MARGIN_MM = 10
CELL_PADDING_MM = 5
TEXT_AREA_MM = 17


def make_qr_image(url: str, *, simple: bool = False):
    error_correction = (
        qrcode.constants.ERROR_CORRECT_L
        if simple
        else qrcode.constants.ERROR_CORRECT_H
    )

    qr = qrcode.QRCode(
        version=None,
        error_correction=error_correction,
        box_size=10,
        border=4,
    )

    qr.add_data(url)
    qr.make(fit=True)

    return qr.make_image(
        fill_color="black",
        back_color="white",
    )


def _qr_image_reader(url: str, *, simple: bool = False) -> ImageReader:
    qr_image = make_qr_image(url, simple=simple)

    qr_buffer = BytesIO()
    qr_image.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)

    return ImageReader(qr_buffer)


def _fit_text(
    text: str,
    *,
    font_name: str,
    font_size: float,
    max_width: float,
) -> str:
    """
    Shorten text with an ellipsis if it does not fit in max_width.
    """
    if stringWidth(text, font_name, font_size) <= max_width:
        return text

    ellipsis = "..."

    while text:
        candidate = text.rstrip() + ellipsis

        if stringWidth(
            candidate,
            font_name,
            font_size,
        ) <= max_width:
            return candidate

        text = text[:-1]

    return ellipsis


def _resolve_qr_mm(
    qr_size: str,
    qr_mm: float | None,
) -> float:
    if qr_mm is None:
        try:
            qr_mm = QR_SIZE_PRESETS_MM[qr_size]
        except KeyError as exc:
            raise ValueError(
                f"Unknown QR size preset: {qr_size}"
            ) from exc

    if qr_mm <= 0:
        raise ValueError("QR size must be greater than zero.")

    return qr_mm


def _draw_label(
    *,
    pdf: canvas.Canvas,
    asset_id: str,
    title: str,
    url: str,
    x: float,
    y: float,
    width: float,
    height: float,
    qr_mm: float,
    simple_qr: bool = False,
) -> None:
    qr_points = qr_mm * mm

    qr_x = x + (width - qr_points) / 2
    qr_y = y + height - qr_points - (2 * mm)

    pdf.drawImage(
        _qr_image_reader(url, simple=simple_qr),
        qr_x,
        qr_y,
        width=qr_points,
        height=qr_points,
        preserveAspectRatio=True,
        mask="auto",
    )

    text_width = width - (4 * mm)
    center_x = x + (width / 2)

    asset_text = _fit_text(
        asset_id,
        font_name="Helvetica-Bold",
        font_size=11,
        max_width=text_width,
    )

    title_text = _fit_text(
        title,
        font_name="Helvetica",
        font_size=8,
        max_width=text_width,
    )

    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawCentredString(
        center_x,
        qr_y - (5 * mm),
        asset_text,
    )

    pdf.setFont("Helvetica", 8)
    pdf.drawCentredString(
        center_x,
        qr_y - (10 * mm),
        title_text,
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
    """
    Generate a single-label A4 PDF.

    Printed label anatomy:
    - QR code
    - Asset ID
    - short title

    The human-readable URL is intentionally not printed.
    """
    simple_qr = qr_size == "tiny" or qr_mm is not None
    qr_mm = _resolve_qr_mm(qr_size, qr_mm)

    output_path = Path(output_path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    pdf = canvas.Canvas(
        str(output_path),
        pagesize=A4,
    )

    page_width, page_height = A4

    qr_points = qr_mm * mm
    label_width = max(
        qr_points + (2 * CELL_PADDING_MM * mm),
        45 * mm,
    )
    label_height = (
        qr_points
        + (TEXT_AREA_MM * mm)
        + (2 * mm)
    )

    x = (page_width - label_width) / 2
    y = page_height - label_height - (20 * mm)

    _draw_label(
    pdf=pdf,
    asset_id=asset_id,
    title=title,
    url=url,
    x=x,
    y=y,
    width=label_width,
    height=label_height,
    qr_mm=qr_mm,
    simple_qr=simple_qr,
)

    pdf.showPage()
    pdf.save()

    return output_path


def generate_batch_label_pdf(
    *,
    labels: list[tuple[str, str, str]],
    output_path: Path,
    qr_size: str = "medium",
    qr_mm: float | None = None,
) -> Path:
    """
    Generate one or more packed A4 pages of QR labels.

    Each label tuple contains:

        (asset_id, title, url)

    Labels are packed left-to-right, then top-to-bottom.
    """
    if not labels:
        raise ValueError("At least one label is required.")

    simple_qr = qr_size == "tiny" or qr_mm is not None
    qr_mm = _resolve_qr_mm(qr_size, qr_mm)

    output_path = Path(output_path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    page_width, page_height = A4

    margin = PAGE_MARGIN_MM * mm
    usable_width = page_width - (2 * margin)
    usable_height = page_height - (2 * margin)

    qr_points = qr_mm * mm

    cell_width = max(
        qr_points + (2 * CELL_PADDING_MM * mm),
        45 * mm,
    )

    cell_height = (
        qr_points
        + (TEXT_AREA_MM * mm)
        + (2 * mm)
    )

    columns = int(usable_width // cell_width)
    rows = int(usable_height // cell_height)

    if columns < 1 or rows < 1:
        raise ValueError(
            "Selected QR size is too large for an A4 page."
        )

    labels_per_page = columns * rows

    grid_width = columns * cell_width
    grid_height = rows * cell_height

    origin_x = (page_width - grid_width) / 2
    origin_y = (page_height + grid_height) / 2

    pdf = canvas.Canvas(
        str(output_path),
        pagesize=A4,
    )

    for index, (asset_id, title, url) in enumerate(labels):
        page_index = index % labels_per_page

        if index > 0 and page_index == 0:
            pdf.showPage()

        row = page_index // columns
        column = page_index % columns

        x = origin_x + (column * cell_width)
        y = (
            origin_y
            - ((row + 1) * cell_height)
        )

        _draw_label(
            pdf=pdf,
            asset_id=asset_id,
            title=title,
            url=url,
            x=x,
            y=y,
            width=cell_width,
            height=cell_height,
            qr_mm=qr_mm,
            simple_qr=simple_qr,
        )

    pdf.showPage()
    pdf.save()

    return output_path