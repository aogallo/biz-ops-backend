from datetime import datetime
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate


class PDFGenerator:
    """Generate PDF file."""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.page_width = letter[0]
        self.page_height = letter[1]

    def generate_pdf(
        self,
        elements: list,
        page_size: tuple[float, float] | None = None,
        rightMargin: float | None = None,
        leftMargin: float | None = None,
        topMargin: float | None = None,
        bottomMargin: float | None = None,
    ) -> bytes:
        buffer = BytesIO()

        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=page_size or letter,
            rightMargin=(rightMargin or 0.75) * inch,
            leftMargin=(leftMargin or 0.75) * inch,
            topMargin=(topMargin or 0.75) * inch,
            bottomMargin=(bottomMargin or 0.75) * inch,
        )

        # Build PDF
        doc.build(elements)

        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes

    def format_date_range(
        self, start_date: datetime | None, end_date: datetime | None
    ) -> str:
        """Format date range for display."""
        # Spanish month names
        months = {
            1: "ENERO",
            2: "FEBRERO",
            3: "MARZO",
            4: "ABRIL",
            5: "MAYO",
            6: "JUNIO",
            7: "JULIO",
            8: "AGOSTO",
            9: "SEPTIEMBRE",
            10: "OCTUBRE",
            11: "NOVIEMBRE",
            12: "DICIEMBRE",
        }

        if start_date and end_date:
            # If same month, show "MONTH YEAR"
            if (
                start_date.month == end_date.month
                and start_date.year == end_date.year
            ):
                month_name = months[start_date.month]
                return f"{month_name} {start_date.year}"
            else:
                # Different months, show range
                start_str = start_date.strftime("%d/%m/%Y")
                end_str = end_date.strftime("%d/%m/%Y")
                return f"{start_str} - {end_str}"
        elif start_date:
            start_str = start_date.strftime("%d/%m/%Y")
            return f"Desde {start_str}"
        elif end_date:
            end_str = end_date.strftime("%d/%m/%Y")
            return f"Hasta {end_str}"
        else:
            return "TODOS LOS PERÍODOS"
