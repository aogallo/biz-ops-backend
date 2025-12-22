from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table

from app.internal.report.pdf_generator import PDFGenerator
from app.internal.report.schemas import SalesLedgerReport


class SalesLedgerPDFGenerator:
    """Generator for sale ledger PDF report."""

    def __init__(self) -> None:
        self.styles = getSampleStyleSheet()
        self.pdf_generator = PDFGenerator()

    def _create_header(
        self,
        company_name: str,
        start_date: datetime | None,
        end_date: datetime | None,
    ) -> list:
        """Create PDF header with company info and report title."""
        elements = []

        from reportlab.lib.styles import ParagraphStyle

        centered_title = ParagraphStyle(
            "CenteredTitle",
            parent=self.styles["Title"],
            alignment=TA_CENTER,
            fontSize=15,
            fontName="Helvetica-Bold",
            spaceAfter=6,
        )

        centered_normal = ParagraphStyle(
            "CenteredNormal",
            parent=self.styles["Normal"],
            alignment=TA_CENTER,
            fontSize=10,
            spaceAfter=12,
        )

        company_paragrah = Paragraph(company_name.upper(), centered_title)
        elements.append(company_paragrah)

        report_title = Paragraph(
            "reporte de ventas - debito fiscal".upper(), centered_normal
        )
        elements.append(report_title)

        date_range_text = self.pdf_generator.format_date_range(
            start_date=start_date,
            end_date=end_date,
        )

        date_title = Paragraph(date_range_text, centered_normal)
        elements.append(date_title)

        return elements

    def _create_entries_table(self, report_data: SalesLedgerReport) -> Table:
        """Create table with sales entries."""
        from reportlab.lib.styles import ParagraphStyle

        header_style = ParagraphStyle(
            name="HeaderTable",
            alignment=TA_CENTER,
            parent=self.styles["Normal"],
        )
        concept_style = ParagraphStyle(
            "ConceptStyle",
            parent=self.styles["Normal"],
            # fontSize=8,
            leading=10,  # Line height
            wordWrap="CJK",  # Enable word wrapping
        )

        cell_style = ParagraphStyle(
            "ConceptStyle",
            parent=self.styles["Normal"],
            fontSize=8,
            leading=10,  # Line height
            wordWrap="CJK",  # Enable word wrapping
        )

        # Table data
        data = []
        header_level_1 = Paragraph("Local", header_style)
        header_level_1_1 = Paragraph("Importación", header_style)

        header_gravados = Paragraph("Gravados", header_style)
        header_exentos = Paragraph("Exentos", header_style)
        data.append(
            [
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                header_level_1,
                "",
                "",
                "",
                header_level_1_1,
                "",
                "",
                "",
                "",
                "",
            ]
        )

        data.append(
            [
                Paragraph("Fecha", concept_style),
                Paragraph("Tipo Doc", concept_style),
                Paragraph("Tipo Transacción", concept_style),
                Paragraph("Serie", concept_style),
                Paragraph("No.Docto", concept_style),
                Paragraph("Nit", concept_style),
                Paragraph("Nombre", concept_style),
                header_gravados,
                "",
                header_exentos,
                "",
                header_gravados,
                "",
                header_exentos,
                "",
                Paragraph("Iva Debito Fiscal", concept_style),
                Paragraph("Total Documento", concept_style),
            ]
        )
        data.append(
            [
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                Paragraph("Bienes", concept_style),
                Paragraph("Servicios", concept_style),
                Paragraph("Bienes", concept_style),
                Paragraph("Servicios", concept_style),
                Paragraph("Bienes", concept_style),
                Paragraph("Servicios", concept_style),
                Paragraph("Bienes", concept_style),
                Paragraph("Servicios", concept_style),
                "",
                "",
            ]
        )

        for entry in report_data.entries:
            row = [
                Paragraph(entry.date.strftime("%d/%m/%Y"), cell_style),
                Paragraph(entry.type, cell_style),
                Paragraph(entry.transaction_type, cell_style),
                Paragraph(entry.serie, cell_style),
                Paragraph(entry.number_doc, cell_style),
                Paragraph(entry.nit, cell_style),
                Paragraph(entry.name, cell_style),
                # Classification amounts (8 columns)
                Paragraph(f"{entry.locally_taxed_goods:,.2f}", cell_style),
                Paragraph(f"{entry.locally_taxed_services:,.2f}", cell_style),
                Paragraph(f"{entry.locally_exempt_goods:,.2f}", cell_style),
                Paragraph(f"{entry.locally_exempt_services:,.2f}", cell_style),
                Paragraph(f"{entry.imported_taxed_goods:,.2f}", cell_style),
                Paragraph(f"{entry.imported_taxed_services:,.2f}", cell_style),
                Paragraph(f"{entry.imported_exempt_goods:,.2f}", cell_style),
                Paragraph(
                    f"{entry.imported_exempt_services:,.2f}", cell_style
                ),
                # IVA and Total
                Paragraph(f"{entry.iva:,.2f}", cell_style),
                Paragraph(f"{entry.total:,.2f}", cell_style),
            ]
            data.append(row)

        # Create table
        table = Table(
            data=data,
            style=[
                # Borders for the table
                ("GRID", (7, 0), (14, -1), 1, colors.black),
                ("GRID", (0, 1), (-1, -1), 1, colors.black),
                # Styles for the first headers (Local, Importación)
                ("SPAN", (7, 0), (10, 0)),
                ("SPAN", (11, 0), (14, 0)),
                # Styles for the first headers (Fecha,...,Nombre)
                ("SPAN", (0, 1), (0, 2)),
                ("SPAN", (1, 1), (1, 2)),
                ("SPAN", (2, 1), (2, 2)),
                ("SPAN", (3, 1), (3, 2)),
                ("SPAN", (4, 1), (4, 2)),
                ("SPAN", (5, 1), (5, 2)),
                ("SPAN", (6, 1), (6, 2)),
                # Styles for the first headers (IVA,Total)
                ("SPAN", (15, 1), (15, 2)),
                ("SPAN", (16, 1), (16, 2)),
                # Styles for the first headers (Gravados,Exentos)
                ("SPAN", (7, 1), (8, 1)),
                ("SPAN", (9, 1), (10, 1)),
                ("SPAN", (11, 1), (12, 1)),
                ("SPAN", (13, 1), (14, 1)),
            ],
        )
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
        Generate PDF for sales journal report.

        Args:
            report_data: Report data with invoices

        Retruns:
            PDF as bytes
        """
        # Built PDF Content
        elements = []

        elements.extend(
            self._create_header(
                company_name=company_name,
                start_date=start_date,
                end_date=end_date,
            )
        )

        if report_data.entries:
            table = self._create_entries_table(report_data=report_data)
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

        pdf_bytes = self.pdf_generator.generate_pdf(
            elements=elements,
            page_size=landscape(letter),
            rightMargin=0.1,
            leftMargin=0.1,
        )

        return pdf_bytes
