"""Professional PDF Report Generator using ReportLab.

Produces formatted executive PDF reports for Value-Based Care ACO performance.
"""

from __future__ import annotations
import io
from datetime import datetime
from typing import Any, Dict

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class NumberedCanvas(canvas.Canvas):
    """Canvas for adding page numbers and running headers/footers."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._saved_page_states: list[Any] = []

    def showPage(self) -> None:
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self) -> None:
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int) -> None:
        if self._pageNumber == 1:
            # Suppress header/footer on cover page
            return

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Header
        self.drawString(54, 750, "VBC CommandIQ — ACO Executive Performance Report")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 744, 558, 744)

        # Footer
        self.line(54, 50, 558, 50)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 38, page_text)
        self.drawString(54, 38, "CONFIDENTIAL — For Internal Payer/ACO Executive Review Only")
        self.restoreState()


class PdfReportService:
    """Generates executive PDF performance reports from aggregated report data."""

    def generate_pdf(self, report_data: Dict[str, Any]) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=54,
            rightMargin=54,
            topMargin=54,
            bottomMargin=54,
        )

        styles = getSampleStyleSheet()

        # Custom Palette
        navy = colors.HexColor("#1E3A8A")
        slate = colors.HexColor("#334155")
        light_bg = colors.HexColor("#F8FAFC")
        accent_blue = colors.HexColor("#2563EB")
        border_color = colors.HexColor("#CBD5E1")
        green = colors.HexColor("#166534")
        red = colors.HexColor("#991B1B")

        # Custom Typography Styles
        cover_title_style = ParagraphStyle(
            "CoverTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=28,
            textColor=navy,
            spaceAfter=10,
        )
        cover_subtitle_style = ParagraphStyle(
            "CoverSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=12,
            leading=16,
            textColor=slate,
            spaceAfter=20,
        )
        section_heading_style = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=navy,
            spaceBefore=14,
            spaceAfter=8,
        )
        sub_heading_style = ParagraphStyle(
            "SubHeading",
            parent=styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=slate,
            spaceBefore=10,
            spaceAfter=4,
        )
        body_style = ParagraphStyle(
            "BodyTextCustom",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13.5,
            textColor=colors.HexColor("#1E293B"),
            spaceAfter=6,
        )
        body_bold = ParagraphStyle(
            "BodyBoldCustom",
            parent=body_style,
            fontName="Helvetica-Bold",
        )
        table_cell_style = ParagraphStyle(
            "TableCell",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#0F172A"),
        )
        table_header_style = ParagraphStyle(
            "TableHeader",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=12,
            textColor=colors.white,
        )

        story: list[Any] = []

        # Data extraction
        data = report_data.get("data", {})
        narrative = report_data.get("narrative", {})
        aco_id = str(report_data.get("aco_id", "A1001"))
        year = str(report_data.get("performance_year", 2024))
        profile = data.get("profile", {})
        fin = data.get("financial", {})
        qual = data.get("quality", {})
        util = data.get("utilization", {})
        pop = data.get("population", {})
        seg = data.get("ml_segmentation", {})
        anom = data.get("ml_anomaly", {})

        aco_name = profile.get("ACO_Name", f"ACO {aco_id}")

        # -------------------------------------------------------------
        # 1. COVER / HEADER BANNER
        # -------------------------------------------------------------
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"ACO Performance & Value-Based Care Report", cover_title_style))
        story.append(Paragraph(f"Contract Analytics & Executive Assessment — {aco_name} ({aco_id})", cover_subtitle_style))
        story.append(HRFlowable(width="100%", thickness=2, color=navy, spaceBefore=0, spaceAfter=15))

        # Metadata Summary Card
        meta_table_data = [
            [
                Paragraph("<b>ACO Identifier:</b>", table_cell_style),
                Paragraph(aco_id, table_cell_style),
                Paragraph("<b>Performance Year:</b>", table_cell_style),
                Paragraph(str(year), table_cell_style),
            ],
            [
                Paragraph("<b>ACO Name:</b>", table_cell_style),
                Paragraph(aco_name, table_cell_style),
                Paragraph("<b>Report Date:</b>", table_cell_style),
                Paragraph(datetime.now().strftime("%B %d, %Y"), table_cell_style),
            ],
            [
                Paragraph("<b>Agreement Track:</b>", table_cell_style),
                Paragraph(str(profile.get("Agree_Type", "Standard")), table_cell_style),
                Paragraph("<b>Risk Model:</b>", table_cell_style),
                Paragraph(str(profile.get("Risk_Model", "Two-Sided")), table_cell_style),
            ],
        ]
        meta_table = Table(meta_table_data, colWidths=[110, 142, 110, 142])
        meta_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), light_bg),
                ("BOX", (0, 0), (-1, -1), 1, border_color),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("PADDING", (0, 0), (-1, -1), 6),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ])
        )
        story.append(meta_table)
        story.append(Spacer(1, 15))

        # -------------------------------------------------------------
        # 2. EXECUTIVE SUMMARY
        # -------------------------------------------------------------
        story.append(Paragraph("1. Executive Summary", section_heading_style))
        headline = narrative.get("headline", f"Executive evaluation for {aco_name} in performance year {year}.")
        story.append(Paragraph(headline, body_style))

        overall_status = narrative.get("overall_status", "GOOD")
        overall_score = narrative.get("overall_score", qual.get("quality_score") or "N/A")

        exec_kpis = [
            [
                Paragraph("<b>Overall Status</b>", table_header_style),
                Paragraph("<b>Quality Score</b>", table_header_style),
                Paragraph("<b>Gross Savings / (Loss)</b>", table_header_style),
                Paragraph("<b>Earned Shared Savings</b>", table_header_style),
            ],
            [
                Paragraph(f"<font color='{green if overall_status == 'GOOD' else red}'><b>{overall_status}</b></font>", table_cell_style),
                Paragraph(f"<b>{overall_score}%</b>" if isinstance(overall_score, (int, float)) else f"<b>{overall_score}</b>", table_cell_style),
                Paragraph(f"<b>${fin.get('GenSaveLoss', 0):,.0f}</b>" if fin.get("GenSaveLoss") is not None else "Not Available", table_cell_style),
                Paragraph(f"<b>${fin.get('EarnSaveLoss', 0):,.0f}</b>" if fin.get("EarnSaveLoss") is not None else "Not Available", table_cell_style),
            ],
        ]
        exec_table = Table(exec_kpis, colWidths=[126, 126, 126, 126])
        exec_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), navy),
                ("BACKGROUND", (0, 1), (-1, 1), light_bg),
                ("BOX", (0, 0), (-1, -1), 1, border_color),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ])
        )
        story.append(exec_table)
        story.append(Spacer(1, 12))

        # Key Strengths & Concerns
        strengths = narrative.get("strengths", [])
        concerns = narrative.get("concerns", [])
        if strengths or concerns:
            story.append(Paragraph("<b>Key Strengths:</b>", sub_heading_style))
            for s in strengths:
                story.append(Paragraph(f"• {s}", body_style))
            story.append(Paragraph("<b>Areas Requiring Attention:</b>", sub_heading_style))
            for c in concerns:
                story.append(Paragraph(f"• {c}", body_style))
            story.append(Spacer(1, 10))

        # -------------------------------------------------------------
        # 3. FINANCIAL PERFORMANCE SECTION
        # -------------------------------------------------------------
        story.append(Paragraph("2. Financial Performance & Benchmark Analysis", section_heading_style))
        fin_insight = narrative.get("financial_insight", "Financial performance analysis based on database benchmark records.")
        story.append(Paragraph(fin_insight, body_style))

        bm_val = fin.get("ABtotBnchmk")
        exp_val = fin.get("ABtotExp")
        gsl_val = fin.get("GenSaveLoss")
        sav_pct = fin.get("SavingsLossPct")
        pmpm = fin.get("PMPM")
        bm_pmpm = fin.get("BenchmarkPMPM")
        earned = fin.get("EarnSaveLoss")

        fin_table_data = [
            [Paragraph("Financial Metric", table_header_style), Paragraph("Database Value", table_header_style), Paragraph("Description / Status", table_header_style)],
            [Paragraph("Risk-Adjusted Benchmark Expenditure", table_cell_style), Paragraph(f"${bm_val:,.0f}" if bm_val else "Not Available", table_cell_style), Paragraph("CMS target baseline spend", table_cell_style)],
            [Paragraph("Actual Total Expenditure", table_cell_style), Paragraph(f"${exp_val:,.0f}" if exp_val else "Not Available", table_cell_style), Paragraph("Total actual claims spend", table_cell_style)],
            [Paragraph("Gross Savings / (Loss)", table_cell_style), Paragraph(f"${gsl_val:,.0f}" if gsl_val else "Not Available", table_cell_style), Paragraph("Benchmark minus Actual Spend", table_cell_style)],
            [Paragraph("Savings / (Loss) Percentage", table_cell_style), Paragraph(f"{sav_pct:.2f}%" if sav_pct is not None else "Not Available", table_cell_style), Paragraph("Gross savings rate", table_cell_style)],
            [Paragraph("Actual PMPM Spend", table_cell_style), Paragraph(f"${pmpm:,.2f}" if pmpm else "Not Available", table_cell_style), Paragraph("Per Member Per Month spend", table_cell_style)],
            [Paragraph("Benchmark PMPM Target", table_cell_style), Paragraph(f"${bm_pmpm:,.2f}" if bm_pmpm else "Not Available", table_cell_style), Paragraph("Per Member Per Month target", table_cell_style)],
            [Paragraph("Earned Shared Savings Payout", table_cell_style), Paragraph(f"${earned:,.0f}" if earned else "Not Available", table_cell_style), Paragraph("Final shared savings distribution", table_cell_style)],
        ]
        fin_table = Table(fin_table_data, colWidths=[180, 140, 184])
        fin_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), navy),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light_bg]),
                ("BOX", (0, 0), (-1, -1), 1, border_color),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("PADDING", (0, 0), (-1, -1), 5),
            ])
        )
        story.append(fin_table)
        story.append(Spacer(1, 15))

        # -------------------------------------------------------------
        # 4. QUALITY & UTILIZATION SECTION
        # -------------------------------------------------------------
        story.append(Paragraph("3. Quality & Utilization Performance", section_heading_style))
        qual_score_val = qual.get("quality_score")
        adm_val = util.get("admissions_per_beneficiary")
        ed_val = util.get("ed_visits_per_beneficiary")

        qu_insight = narrative.get("quality_insight", "Quality and utilization metrics retrieved from database records.")
        story.append(Paragraph(qu_insight, body_style))

        qu_data = [
            [Paragraph("Performance Metric", table_header_style), Paragraph("Value", table_header_style), Paragraph("Category / Benchmark", table_header_style)],
            [Paragraph("Composite Quality Score", table_cell_style), Paragraph(f"{qual_score_val:.2f}%" if qual_score_val is not None else "Not Available", table_cell_style), Paragraph("Tier 1 Quality Bonus Eligible" if qual_score_val and qual_score_val >= 85 else "Standard", table_cell_style)],
            [Paragraph("Inpatient Admissions (per ben. / 1k)", table_cell_style), Paragraph(f"{adm_val:.4f}" if adm_val is not None else "Not Available", table_cell_style), Paragraph("Hospital admission rate", table_cell_style)],
            [Paragraph("Emergency Dept Visits (per ben. / 1k)", table_cell_style), Paragraph(f"{ed_val:.4f}" if ed_val is not None else "Not Available", table_cell_style), Paragraph("ED visit rate", table_cell_style)],
            [Paragraph("Attributed Beneficiaries (N_AB)", table_cell_style), Paragraph(f"{pop.get('assigned_beneficiaries', 'Not Available'):,}" if isinstance(pop.get('assigned_beneficiaries'), (int, float)) else "Not Available", table_cell_style), Paragraph("Aligned beneficiary count", table_cell_style)],
        ]
        qu_table = Table(qu_data, colWidths=[180, 140, 184])
        qu_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), navy),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light_bg]),
                ("BOX", (0, 0), (-1, -1), 1, border_color),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("PADDING", (0, 0), (-1, -1), 5),
            ])
        )
        story.append(qu_table)
        story.append(Spacer(1, 15))

        # -------------------------------------------------------------
        # 5. ML RISK & ANOMALY ASSESSMENT
        # -------------------------------------------------------------
        story.append(Paragraph("4. ML Risk & Anomaly Assessment", section_heading_style))
        cluster_seg = seg.get("performance_segment", "Standard")
        anom_score = anom.get("ml_anomaly_score", 0.0)
        is_anom = anom.get("is_anomaly", False)

        ml_table_data = [
            [Paragraph("ML Evaluation Component", table_header_style), Paragraph("Model Output", table_header_style), Paragraph("Risk Level", table_header_style)],
            [Paragraph("Performance Segmentation Cluster", table_cell_style), Paragraph(str(cluster_seg), table_cell_style), Paragraph("Segment Assigned", table_cell_style)],
            [Paragraph("Isolation Forest Anomaly Score", table_cell_style), Paragraph(f"{anom_score:.2f}", table_cell_style), Paragraph("<font color='red'>HIGH ANOMALY</font>" if is_anom else "<font color='green'>LOW ANOMALY</font>", table_cell_style)],
        ]
        ml_table = Table(ml_table_data, colWidths=[180, 140, 184])
        ml_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), navy),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light_bg]),
                ("BOX", (0, 0), (-1, -1), 1, border_color),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("PADDING", (0, 0), (-1, -1), 5),
            ])
        )
        story.append(ml_table)
        story.append(Spacer(1, 15))

        # -------------------------------------------------------------
        # 6. AI GROUNDED RECOMMENDATIONS
        # -------------------------------------------------------------
        recs = narrative.get("recommendations", [])
        if recs:
            story.append(Paragraph("5. AI Grounded Actionable Recommendations", section_heading_style))
            rec_headers = [Paragraph("Priority", table_header_style), Paragraph("Issue / Area", table_header_style), Paragraph("Evidence", table_header_style), Paragraph("Recommended Action", table_header_style)]
            rec_rows = [rec_headers]
            for r in recs:
                prio = r.get("priority", "MEDIUM")
                prio_color = red if prio == "HIGH" else (colors.HexColor("#D97706") if prio == "MEDIUM" else green)
                rec_rows.append([
                    Paragraph(f"<font color='{prio_color}'><b>{prio}</b></font>", table_cell_style),
                    Paragraph(str(r.get("issue", "")), table_cell_style),
                    Paragraph(str(r.get("evidence", "")), table_cell_style),
                    Paragraph(str(r.get("action", "")), table_cell_style),
                ])
            rec_table = Table(rec_rows, colWidths=[64, 130, 130, 180])
            rec_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), navy),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light_bg]),
                    ("BOX", (0, 0), (-1, -1), 1, border_color),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                    ("PADDING", (0, 0), (-1, -1), 5),
                ])
            )
            story.append(rec_table)
            story.append(Spacer(1, 15))

        # -------------------------------------------------------------
        # 6. AI INSIGHTS & RECOMMENDATIONS (ACO & YEAR SPECIFIC)
        # -------------------------------------------------------------
        story.append(Paragraph("6. AI Insights & Recommendations", section_heading_style))
        story.append(Paragraph("<font size=8 color='#64748B'><i>Generated from ACO-specific performance data &amp; ML Anomaly Analytics</i></font>", body_style))
        story.append(Spacer(1, 4))

        ai_insights = data.get("ai_insights", {})
        if not ai_insights:
            ai_insights = narrative.get("ai_insights", {})

        assessment = ai_insights.get("overall_assessment") or narrative.get("headline") or "Detailed performance analysis generated for this ACO."
        story.append(Paragraph("<b>Overall Performance Assessment</b>", sub_heading_style))
        story.append(Paragraph(f"{assessment}", body_style))
        story.append(Spacer(1, 6))

        # Strengths
        strengths = ai_insights.get("strengths") or narrative.get("strengths") or []
        if strengths:
            story.append(Paragraph("<b>Key Strengths:</b>", sub_heading_style))
            for s in strengths:
                story.append(Paragraph(f"• <font color='#059669'><b>[Strength]</b></font> {s}", body_style))
            story.append(Spacer(1, 6))

        # Areas Requiring Improvement
        improvements = ai_insights.get("areas_requiring_improvement") or narrative.get("concerns") or []
        if improvements:
            story.append(Paragraph("<b>Areas Requiring Improvement:</b>", sub_heading_style))
            for imp in improvements:
                story.append(Paragraph(f"• <font color='#DC2626'><b>[Focus Area]</b></font> {imp}", body_style))
            story.append(Spacer(1, 6))

        # Recommended Actions Table
        actions = ai_insights.get("recommended_actions") or narrative.get("recommendations") or []
        if actions:
            story.append(Paragraph("<b>AI Recommended Actions:</b>", sub_heading_style))
            act_headers = [Paragraph("Priority", table_header_style), Paragraph("Recommended Action", table_header_style)]
            act_rows = [act_headers]
            for act in actions:
                if isinstance(act, dict):
                    prio = act.get("priority", "MEDIUM")
                    action_text = act.get("action", "")
                else:
                    prio = "MEDIUM"
                    action_text = str(act)
                prio_color = red if prio == "HIGH" else (colors.HexColor("#D97706") if prio == "MEDIUM" else green)
                act_rows.append([
                    Paragraph(f"<font color='{prio_color}'><b>{prio}</b></font>", table_cell_style),
                    Paragraph(action_text, table_cell_style),
                ])
            act_table = Table(act_rows, colWidths=[80, 424])
            act_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), navy),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light_bg]),
                    ("BOX", (0, 0), (-1, -1), 1, border_color),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                    ("PADDING", (0, 0), (-1, -1), 5),
                ])
            )
            story.append(act_table)
            story.append(Spacer(1, 6))

        # Next-Year Priorities
        priorities = ai_insights.get("next_year_priorities") or []
        if priorities:
            story.append(Paragraph("<b>Next-Year Executive Priorities:</b>", sub_heading_style))
            for p in priorities:
                story.append(Paragraph(f"• {p}", body_style))
            story.append(Spacer(1, 8))

        # Disclaimer
        disclaimer = ai_insights.get("disclaimer") or "AI-generated insights are decision-support recommendations derived from ACO performance data."
        story.append(Paragraph(f"<font size=7 color='#94A3B8'><b>Disclaimer:</b> {disclaimer}</font>", body_style))

        doc.build(story, canvasmaker=NumberedCanvas)
        buffer.seek(0)
        return buffer.getvalue()
