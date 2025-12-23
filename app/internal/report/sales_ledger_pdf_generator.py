"""Sales Ledger PDF Generator with repeating headers and page numbers."""

from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.internal.report.schemas import SalesLedgerReport


class SalesLedgerPDFGenerator:
    """Generator for sales ledger PDF report with repeating headers."""

    # Global font settings
    FONT_NAME = "Helvetica"
    FONT_SIZE = 7
    HEADER_FONT_SIZE = 8

    def __init__(self) -> None:
        self.styles = getSampleStyleSheet()
        self.company_name = ""
        self.date_range_text = ""
        self.page_width = landscape(letter)[0]
        self.page_height = landscape(letter)[1]

    def _header_footer(self, canvas, doc):
        """Add header and footer to each page."""
        canvas.saveState()

        # Header - Company name
        canvas.setFont(self.FONT_NAME + "-Bold", 12)
        canvas.drawCentredString(
            self.page_width / 2.0,
            self.page_height - 0.5 * inch,
            self.company_name.upper(),
        )

        # Subheader - Report title
        canvas.setFont(self.FONT_NAME, 10)
        canvas.drawCentredString(
            self.page_width / 2.0,
            self.page_height - 0.7 * inch,
            "REPORTE DE VENTAS - DEBITO FISCAL",
        )

        # Date range
        canvas.setFont(self.FONT_NAME, 10)
        canvas.drawCentredString(
            self.page_width / 2.0,
            self.page_height - 0.9 * inch,
            self.date_range_text,
        )

        # Footer - Page number (Folio) - right-aligned
        canvas.setFont(self.FONT_NAME, 9)
        folio_text = f"Folio: {doc.page}"
        canvas.drawRightString(
            self.page_width - 0.5 * inch,
            self.page_height - 0.5 * inch,
            folio_text,
        )

        canvas.restoreState()

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

    def _create_entries_table(self, report_data: SalesLedgerReport) -> Table:
        """Create table with sales entries and repeating headers."""

        # Style for header text (centered, bold, no wrapping)
        header_style = ParagraphStyle(
            name="HeaderStyle",
            alignment=TA_CENTER,
            fontSize=self.HEADER_FONT_SIZE,
            fontName=self.FONT_NAME + "-Bold",
            leading=10,
        )

        # Style for data cells (no wrapping)
        cell_style = ParagraphStyle(
            name="CellStyle",
            fontSize=self.FONT_SIZE,
            fontName=self.FONT_NAME,
            leading=9,
        )

        # Style for centered data cells
        cell_center_style = ParagraphStyle(
            name="CellCenterStyle",
            alignment=TA_CENTER,
            fontSize=self.FONT_SIZE,
            fontName=self.FONT_NAME,
            leading=9,
        )

        # Style for right-aligned numbers
        cell_right_style = ParagraphStyle(
            name="CellRightStyle",
            alignment=TA_RIGHT,
            fontSize=self.FONT_SIZE,
            fontName=self.FONT_NAME,
            leading=9,
        )

        # Table data
        data = []

        # Row 0: Top-level headers (Local, Importación)
        data.append(
            [
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                Paragraph("Local", header_style),
                "",
                "",
                "",
                Paragraph("Importación", header_style),
                "",
                "",
                "",
                "",
                "",
            ]
        )

        # Row 1: Second-level headers (with line breaks for multi-word headers)
        data.append(
            [
                Paragraph("Fecha", header_style),
                Paragraph("Tipo<br/>Doc", header_style),
                Paragraph("Tipo<br/>Transacción", header_style),
                Paragraph("Serie", header_style),
                Paragraph("No.Docto", header_style),
                Paragraph("Nit", header_style),
                Paragraph("Nombre", header_style),
                Paragraph("Gravados", header_style),
                "",
                Paragraph("Exentos", header_style),
                "",
                Paragraph("Gravados", header_style),
                "",
                Paragraph("Exentos", header_style),
                "",
                Paragraph("Iva<br/>Debito<br/>Fiscal", header_style),
                Paragraph("Total<br/>Documento", header_style),
            ]
        )

        # Row 2: Third-level headers (Bienes, Servicios)
        data.append(
            [
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                Paragraph("Bienes", header_style),
                Paragraph("Servicios", header_style),
                Paragraph("Bienes", header_style),
                Paragraph("Servicios", header_style),
                Paragraph("Bienes", header_style),
                Paragraph("Servicios", header_style),
                Paragraph("Bienes", header_style),
                Paragraph("Servicios", header_style),
                "",
                "",
            ]
        )

        # Data rows
        for entry in report_data.entries:
            row = [
                Paragraph(entry.date.strftime("%d/%m/%y"), cell_center_style),
                Paragraph(entry.type, cell_center_style),
                Paragraph(entry.transaction_type, cell_center_style),
                Paragraph(entry.serie, cell_center_style),
                Paragraph(entry.number_doc, cell_center_style),
                Paragraph(entry.nit, cell_center_style),
                Paragraph(entry.name, cell_style),
                # Classification amounts (8 columns) - right aligned
                Paragraph(
                    f"{entry.locally_taxed_goods:.2f}"
                    if entry.locally_taxed_goods
                    else "0.00",
                    cell_right_style,
                ),
                Paragraph(
                    f"{entry.locally_taxed_services:.2f}"
                    if entry.locally_taxed_services
                    else "0.00",
                    cell_right_style,
                ),
                Paragraph(
                    f"{entry.locally_exempt_goods:.2f}"
                    if entry.locally_exempt_goods
                    else "0.00",
                    cell_right_style,
                ),
                Paragraph(
                    f"{entry.locally_exempt_services:.2f}"
                    if entry.locally_exempt_services
                    else "0.00",
                    cell_right_style,
                ),
                Paragraph(
                    f"{entry.imported_taxed_goods:.2f}"
                    if entry.imported_taxed_goods
                    else "0.00",
                    cell_right_style,
                ),
                Paragraph(
                    f"{entry.imported_taxed_services:.2f}"
                    if entry.imported_taxed_services
                    else "0.00",
                    cell_right_style,
                ),
                Paragraph(
                    f"{entry.imported_exempt_goods:.2f}"
                    if entry.imported_exempt_goods
                    else "0.00",
                    cell_right_style,
                ),
                Paragraph(
                    f"{entry.imported_exempt_services:.2f}"
                    if entry.imported_exempt_services
                    else "0.00",
                    cell_right_style,
                ),
                # IVA and Total - right aligned
                Paragraph(f"{entry.iva:.2f}", cell_right_style),
                Paragraph(f"{entry.total:.2f}", cell_right_style),
            ]
            data.append(row)

        # Create table with explicit column widths
        table = Table(
            data=data,
            colWidths=[
                0.45 * inch,  # Fecha
                0.42 * inch,  # Tipo Doc (wider for "FACT")
                0.45 * inch,  # Tipo Transacción
                0.38 * inch,  # Serie
                0.48 * inch,  # No.Docto
                0.50 * inch,  # Nit
                1.20 * inch,  # Nombre (reduced to make room)
                0.48 * inch,  # Bienes (Local Gravados)
                0.62
                * inch,  # Servicios (Local Gravados) - wider for "Servicios"
                0.48 * inch,  # Bienes (Local Exentos)
                0.62
                * inch,  # Servicios (Local Exentos) - wider for "Servicios"
                0.48 * inch,  # Bienes (Importación Gravados)
                0.62 * inch,  # Servicios (Importación Gravados) - wider
                0.48 * inch,  # Bienes (Importación Exentos)
                0.62 * inch,  # Servicios (Importación Exentos) - wider
                0.52 * inch,  # Iva Debito Fiscal
                0.55 * inch,  # Total Documento
            ],
            repeatRows=3,  # Repeat first 3 rows (all header rows) on each page
        )

        # Table styling
        table_style = TableStyle(
            [
                # Global font and size
                ("FONTNAME", (0, 0), (-1, -1), self.FONT_NAME),
                ("FONTSIZE", (0, 0), (-1, -1), self.FONT_SIZE),
                # Header font (rows 0-2)
                ("FONTNAME", (0, 0), (-1, 2), self.FONT_NAME + "-Bold"),
                ("FONTSIZE", (0, 0), (-1, 2), self.HEADER_FONT_SIZE),
                # Alignment for headers
                ("ALIGN", (0, 0), (-1, 2), "CENTER"),
                ("VALIGN", (0, 0), (-1, 2), "MIDDLE"),
                # Background for header rows
                ("BACKGROUND", (0, 0), (-1, 2), colors.white),
                # Borders
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("BOX", (0, 0), (-1, -1), 1, colors.black),
                # Thicker borders for header section
                ("LINEBELOW", (0, 2), (-1, 2), 1, colors.black),
                # Row 0 spans (Local, Importación)
                ("SPAN", (7, 0), (10, 0)),  # Local
                ("SPAN", (11, 0), (14, 0)),  # Importación
                # Row 1 spans (Fecha through Nombre, IVA, Total)
                ("SPAN", (0, 1), (0, 2)),  # Fecha
                ("SPAN", (1, 1), (1, 2)),  # Tipo Doc
                ("SPAN", (2, 1), (2, 2)),  # Tipo Transacción
                ("SPAN", (3, 1), (3, 2)),  # Serie
                ("SPAN", (4, 1), (4, 2)),  # No.Docto
                ("SPAN", (5, 1), (5, 2)),  # Nit
                ("SPAN", (6, 1), (6, 2)),  # Nombre
                ("SPAN", (15, 1), (15, 2)),  # IVA
                ("SPAN", (16, 1), (16, 2)),  # Total
                # Row 1 spans (Gravados, Exentos under Local and Importación)
                ("SPAN", (7, 1), (8, 1)),  # Gravados (Local)
                ("SPAN", (9, 1), (10, 1)),  # Exentos (Local)
                ("SPAN", (11, 1), (12, 1)),  # Gravados (Importación)
                ("SPAN", (13, 1), (14, 1)),  # Exentos (Importación)
                # Alignment for data rows
                ("ALIGN", (0, 3), (6, -1), "LEFT"),  # Left align text columns
                (
                    "ALIGN",
                    (7, 3),
                    (-1, -1),
                    "RIGHT",
                ),  # Right align number columns
                ("VALIGN", (0, 3), (-1, -1), "TOP"),
                # Padding - reduced to prevent text wrapping
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
            ]
        )

        table.setStyle(table_style)
        return table

    def generate(
        self,
        report_data: SalesLedgerReport,
        company_name: str,
        company_nit: str,
        start_date: datetime | None,
        end_date: datetime | None,
    ) -> bytes:
        """
        Generate PDF for sales ledger report.

        Args:
            report_data: Report data with invoices
            company_name: Company name for header
            company_nit: Company NIT (not currently used but kept for
                         compatibility)
            start_date: Start date filter (optional)
            end_date: End date filter (optional)

        Returns:
            PDF as bytes
        """
        buffer = BytesIO()

        # Store for header/footer callback
        self.company_name = company_name
        self.date_range_text = self._format_date_range(start_date, end_date)

        # Create PDF document with custom page template
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(letter),
            rightMargin=0.2 * inch,  # Reduced for more table space
            leftMargin=0.2 * inch,  # Reduced for more table space
            topMargin=1.2 * inch,  # More space for header
            bottomMargin=0.5 * inch,
        )

        # Build PDF content
        elements = []

        if report_data.entries:
            table = self._create_entries_table(report_data=report_data)
            elements.append(table)
        else:
            # No data message - Spanish
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
            elements.append(Spacer(1, 2 * inch))
            elements.append(no_data_para)

        # Build PDF with header/footer callback
        doc.build(
            elements,
            onFirstPage=self._header_footer,
            onLaterPages=self._header_footer,
        )

        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes
