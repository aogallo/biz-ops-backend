"""PDF generation utilities for reports."""
from datetime import UTC, datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.internal.report.schemas import GeneralJournalReport


class GeneralJournalPDFGenerator:
    """Generator for General Journal PDF reports."""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.page_width = letter[0]
        self.page_height = letter[1]

    def generate(
        self,
        report_data: GeneralJournalReport,
        company_name: str,
        company_nit: str,
        start_date: datetime | None,
        end_date: datetime | None,
    ) -> bytes:
        """
        Generate PDF for general journal report.

        Args:
            report_data: Report data with entries and totals
            company_name: Company name for header
            company_nit: Company NIT for header
            start_date: Start date filter (optional)
            end_date: End date filter (optional)

        Returns:
            PDF as bytes
        """
        buffer = BytesIO()

        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch,
        )

        # Build PDF content
        elements = []

        # Add header
        elements.extend(
            self._create_header(
                company_name, company_nit, start_date, end_date
            )
        )
        elements.append(Spacer(1, 0.3 * inch))

        # Add table with entries
        if report_data.entries:
            table = self._create_entries_table(report_data)
            elements.append(table)
        else:
            # No data message - Spanish
            from reportlab.lib.enums import TA_CENTER
            from reportlab.lib.styles import ParagraphStyle

            no_data_style = ParagraphStyle(
                "NoData",
                parent=self.styles["Normal"],
                alignment=TA_CENTER,
                fontSize=10,
                textColor=colors.grey,
            )
            no_data_para = Paragraph(
                """<i>No se encontraron registros
                para el período seleccionado.</i>""",
                no_data_style,
            )
            elements.append(no_data_para)

        # Build PDF
        doc.build(elements)

        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes

    def _create_header(
        self,
        company_name: str,
        company_nit: str,
        start_date: datetime | None,
        end_date: datetime | None,
    ) -> list:
        """Create PDF header with company info and report title."""
        elements = []

        # Company name - centered and bold
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.styles import ParagraphStyle

        centered_title = ParagraphStyle(
            "CenteredTitle",
            parent=self.styles["Title"],
            alignment=TA_CENTER,
            fontSize=16,
            fontName="Helvetica-Bold",
            spaceAfter=6,
        )

        company_para = Paragraph(company_name.upper(), centered_title)
        elements.append(company_para)

        # NIT - centered
        centered_normal = ParagraphStyle(
            "CenteredNormal",
            parent=self.styles["Normal"],
            alignment=TA_CENTER,
            fontSize=10,
            spaceAfter=12,
        )
        nit_para = Paragraph(f"NIT: {company_nit}", centered_normal)
        elements.append(nit_para)

        # Report title - centered and bold
        centered_heading = ParagraphStyle(
            "CenteredHeading",
            parent=self.styles["Heading1"],
            alignment=TA_CENTER,
            fontSize=14,
            fontName="Helvetica-Bold",
            spaceAfter=6,
        )

        date_range_text = self._format_date_range(start_date, end_date)
        title_para = Paragraph(
            f"LIBRO DIARIO GENERAL - {date_range_text}", centered_heading
        )
        elements.append(title_para)

        # Generation timestamp - centered, smaller
        centered_small = ParagraphStyle(
            "CenteredSmall",
            parent=self.styles["Normal"],
            alignment=TA_CENTER,
            fontSize=8,
            textColor=colors.grey,
            spaceAfter=12,
        )
        now = datetime.now(UTC)
        gen_time = now.strftime("%Y-%m-%d %H:%M:%S UTC")
        gen_para = Paragraph(f"Generado: {gen_time}", centered_small)
        elements.append(gen_para)

        return elements

    def _format_date_range(
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

    def _create_entries_table(
        self, report_data: GeneralJournalReport
    ) -> Table:
        """Create table with journal entries and totals."""
        from reportlab.lib.styles import ParagraphStyle

        # Style for wrapping text in concept column
        concept_style = ParagraphStyle(
            "ConceptStyle",
            parent=self.styles["Normal"],
            fontSize=8,
            leading=10,  # Line height
            wordWrap="CJK",  # Enable word wrapping
        )

        # Table data
        data = []

        # Header row - Spanish labels to match example
        headers = [
            "FECHA",
            "NO. CUENTA",
            "NOMBRE CUENTA",
            "CONCEPTO",
            "DEBE",
            "HABER",
            "FOLIO",
        ]
        data.append(headers)

        # Entry rows
        for entry in report_data.entries:
            # Wrap concept text in Paragraph for text wrapping
            concept_para = Paragraph(entry.transaction_concept, concept_style)

            row = [
                entry.date.strftime("%d/%m/%Y"),  # dd/mm/yyyy format
                entry.account_number,
                entry.account_name,
                concept_para,  # Use Paragraph instead of plain string
                self._format_currency(entry.debit),
                self._format_currency(entry.credit),
                str(entry.folio_number),
            ]
            data.append(row)

        # Totals row - Spanish label
        totals_row = [
            "",
            "",
            "",
            f"TOTALES ({report_data.count} registros)",
            self._format_currency(report_data.total_debits),
            self._format_currency(report_data.total_credits),
            "",
        ]
        data.append(totals_row)

        # Create table
        table = Table(
            data,
            colWidths=[
                1.0 * inch,  # Date
                0.8 * inch,  # Account #
                1.5 * inch,  # Account Name
                1.8 * inch,  # Concept
                1.0 * inch,  # Debit
                1.0 * inch,  # Credit
                0.6 * inch,  # Folio
            ],
        )

        # Table styling - cleaner, more professional appearance
        table_style = TableStyle(
            [
                # Header row styling - lighter background, better contrast
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8E8E8")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 0), (-1, 0), 8),
                # Data rows styling
                ("FONTNAME", (0, 1), (-1, -2), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -2), 8),
                ("ALIGN", (0, 1), (0, -2), "CENTER"),  # Date centered
                ("ALIGN", (1, 1), (1, -2), "CENTER"),  # Account # centered
                ("ALIGN", (2, 1), (2, -2), "LEFT"),  # Account Name left
                ("ALIGN", (3, 1), (3, -2), "LEFT"),  # Concept left
                ("ALIGN", (4, 1), (4, -2), "RIGHT"),  # Debit right
                ("ALIGN", (5, 1), (5, -2), "RIGHT"),  # Credit right
                ("ALIGN", (6, 1), (6, -2), "CENTER"),  # Folio centered
                (
                    "VALIGN",
                    (0, 1),
                    (-1, -2),
                    "TOP",
                ),  # Vertical align to top for wrapped text
                ("TOPPADDING", (0, 1), (-1, -2), 6),
                ("BOTTOMPADDING", (0, 1), (-1, -2), 6),
                # Subtle alternating row colors for better readability
                *[
                    ("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F8F8F8"))
                    for i in range(2, len(data) - 1, 2)
                ],
                # Totals row styling - more prominent
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#D8D8D8")),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, -1), (-1, -1), 9),
                ("ALIGN", (3, -1), (3, -1), "RIGHT"),
                ("ALIGN", (4, -1), (4, -1), "RIGHT"),
                ("ALIGN", (5, -1), (5, -1), "RIGHT"),
                ("TOPPADDING", (0, -1), (-1, -1), 10),
                ("BOTTOMPADDING", (0, -1), (-1, -1), 10),
                # Clean grid lines - thinner, more subtle
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#C0C0C0")),
                (
                    "LINEBELOW",
                    (0, 0),
                    (-1, 0),
                    1.5,
                    colors.black,
                ),  # Thicker line under header
                (
                    "LINEABOVE",
                    (0, -1),
                    (-1, -1),
                    1.5,
                    colors.black,
                ),  # Thicker line above totals
                ("BOX", (0, 0), (-1, -1), 1, colors.black),
            ]
        )

        table.setStyle(table_style)
        return table

    def _format_currency(self, amount: float) -> str:
        """Format number as currency with Guatemalan Quetzal format."""
        if amount == 0:
            return "-"
        # Format with comma as thousands separator and 2 decimals
        # Example: Q 1,234.56
        return f"Q {amount:,.2f}"
