"""Report generation and export service.

Assembles analytics data and insights into structured reports, with export
support for CSV (lightweight) and PDF (presentation-ready via ReportLab).
"""

import json
import csv
import io
from datetime import datetime

from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from models.forecast import ForecastResult, SavedReport
from services.analytics_service import AnalyticsService
from services.insights_service import InsightsService


class ReportService:

    @staticmethod
    def generate_report(
        db: Session,
        dataset_id: int,
        user_id: int,
        title: str,
        report_type: str,
    ) -> SavedReport:
        """Build a report from analytics + insights and save it to the DB."""
        report_data = {
            'generated_at': datetime.utcnow().isoformat(),
            'kpis': AnalyticsService.get_kpi_metrics(db, dataset_id),
            'top_products': AnalyticsService.get_top_products(db, dataset_id, limit=5),
            'regions': AnalyticsService.get_revenue_by_region(db, dataset_id),
            'categories': AnalyticsService.get_category_performance(db, dataset_id),
            'insights': InsightsService.generate_insights(db, dataset_id),
        }

        # Attach forecast metrics when the report type requests them
        if report_type == 'forecast':
            forecast = (
                db.query(ForecastResult)
                .filter(ForecastResult.dataset_id == dataset_id)
                .order_by(ForecastResult.created_at.desc())
                .first()
            )
            if forecast:
                report_data['forecast'] = {
                    'model_type': forecast.model_type,
                    'rmse': forecast.rmse,
                    'mae': forecast.mae,
                    'r2_score': forecast.r2_score,
                }

        report = SavedReport(
            user_id=user_id,
            title=title,
            report_type=report_type,
            report_data=json.dumps(report_data),
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report

    @staticmethod
    def export_csv(report: SavedReport) -> bytes:
        """Render a saved report as a UTF-8 CSV file."""
        data = json.loads(report.report_data)
        output = io.StringIO()
        writer = csv.writer(output)

        # --- Header ---
        writer.writerow(['Retail Sales Intelligence Report'])
        writer.writerow(['Title', report.title])
        writer.writerow(['Generated', data.get('generated_at', '')])
        writer.writerow([])

        # --- KPIs ---
        kpis = data.get('kpis', {})
        writer.writerow(['Key Performance Indicators'])
        for name, value in kpis.items():
            writer.writerow([name, value])
        writer.writerow([])

        # --- Top Products ---
        writer.writerow(['Product', 'Category', 'Revenue', 'Quantity'])
        for p in data.get('top_products', []):
            writer.writerow([
                p.get('product_name', ''),
                p.get('category', ''),
                p.get('revenue', ''),
                p.get('quantity', ''),
            ])
        writer.writerow([])

        # --- Regional Performance ---
        writer.writerow(['Region', 'Revenue', 'Profit', 'Orders'])
        for r in data.get('regions', []):
            writer.writerow([
                r.get('region', ''),
                r.get('revenue', ''),
                r.get('profit', ''),
                r.get('orders', ''),
            ])

        return output.getvalue().encode('utf-8')

    # ------------------------------------------------------------------ #
    #  Shared table style used by all PDF tables                          #
    # ------------------------------------------------------------------ #
    _TABLE_STYLE = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f0f5')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])

    @staticmethod
    def export_pdf(report: SavedReport) -> bytes:
        """Render a saved report as a styled PDF document."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=20,
            textColor=colors.HexColor('#1a1a2e'),
        )
        section_style = ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            textColor=colors.HexColor('#16213e'),
        )

        elements = []
        data = json.loads(report.report_data)

        # --- Title block ---
        elements.append(Paragraph(report.title, title_style))
        elements.append(
            Paragraph('Retail Sales Intelligence Platform', styles['Normal'])
        )
        elements.append(
            Paragraph(
                f'Generated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M")}',
                styles['Normal'],
            )
        )
        elements.append(Spacer(1, 0.3 * inch))

        # --- KPI Summary ---
        elements.append(Paragraph('Key Performance Indicators', section_style))
        kpis = data.get('kpis', {})
        kpi_table_data = [
            ['Metric', 'Value'],
            ['Total Revenue', f"${kpis.get('total_revenue', 0):,.2f}"],
            ['Total Profit', f"${kpis.get('total_profit', 0):,.2f}"],
            ['Total Orders', str(kpis.get('total_orders', 0))],
            ['Avg Order Value', f"${kpis.get('avg_order_value', 0):,.2f}"],
            ['Profit Margin', f"{kpis.get('overall_profit_margin', 0):.1f}%"],
            ['Unique Customers', str(kpis.get('unique_customers', 0))],
        ]
        kpi_table = Table(kpi_table_data, hAlign='LEFT')
        kpi_table.setStyle(ReportService._TABLE_STYLE)
        elements.append(kpi_table)
        elements.append(Spacer(1, 0.3 * inch))

        # --- Top Products ---
        elements.append(Paragraph('Top Products', section_style))
        product_rows = [['Product Name', 'Category', 'Revenue']]
        for p in data.get('top_products', []):
            product_rows.append([
                p.get('product_name', ''),
                p.get('category', ''),
                f"${p.get('revenue', 0):,.2f}",
            ])
        product_table = Table(product_rows, hAlign='LEFT')
        product_table.setStyle(ReportService._TABLE_STYLE)
        elements.append(product_table)
        elements.append(Spacer(1, 0.3 * inch))

        # --- Regional Performance ---
        elements.append(Paragraph('Regional Performance', section_style))
        region_rows = [['Region', 'Revenue', 'Profit', 'Orders']]
        for r in data.get('regions', []):
            region_rows.append([
                r.get('region', ''),
                f"${r.get('revenue', 0):,.2f}",
                f"${r.get('profit', 0):,.2f}",
                str(r.get('orders', 0)),
            ])
        region_table = Table(region_rows, hAlign='LEFT')
        region_table.setStyle(ReportService._TABLE_STYLE)
        elements.append(region_table)
        elements.append(Spacer(1, 0.3 * inch))

        # --- Business Insights ---
        elements.append(Paragraph('Business Insights', section_style))
        for insight in data.get('insights', []):
            elements.append(
                Paragraph(
                    f"&bull; {insight.get('title', '')}: "
                    f"{insight.get('description', '')}",
                    styles['Normal'],
                )
            )
            elements.append(Spacer(1, 0.1 * inch))

        doc.build(elements)
        return buffer.getvalue()
