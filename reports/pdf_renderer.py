import logging
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from config.settings import settings

logger = logging.getLogger(__name__)

NAVY       = colors.HexColor("#1a2340")
SLATE      = colors.HexColor("#2d3a56")
ACCENT     = colors.HexColor("#2563eb")
LIGHT_BLUE = colors.HexColor("#eff6ff")
LIGHT_GRAY = colors.HexColor("#f8fafc")
BORDER     = colors.HexColor("#e2e8f0")
TEXT_DARK  = colors.HexColor("#0f172a")
TEXT_MID   = colors.HexColor("#334155")
TEXT_LIGHT = colors.HexColor("#64748b")
WHITE      = colors.white
HIGH_RED   = colors.HexColor("#dc2626")
MED_AMBER  = colors.HexColor("#d97706")
LOW_GREEN  = colors.HexColor("#16a34a")
GOLD       = colors.HexColor("#f59e0b")
TEAL       = colors.HexColor("#0d9488")
PURPLE     = colors.HexColor("#7c3aed")

class PDFRenderer:

    def __init__(self):
        self.output_dir = settings.REPORT_OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.styles = self._build_styles()

    def _build_styles(self) -> dict:
        return {
            "cover_title": ParagraphStyle("cover_title", fontName="Helvetica-Bold",
                fontSize=28, textColor=WHITE, leading=36, alignment=TA_LEFT),
            "cover_sub": ParagraphStyle("cover_sub", fontName="Helvetica",
                fontSize=13, textColor=colors.HexColor("#94a3b8"), leading=20),
            "section_header": ParagraphStyle("section_header", fontName="Helvetica-Bold",
                fontSize=14, textColor=NAVY, leading=20, spaceBefore=20, spaceAfter=8),
            "subsection_header": ParagraphStyle("subsection_header", fontName="Helvetica-Bold",
                fontSize=11, textColor=SLATE, leading=16, spaceBefore=12, spaceAfter=4),
            "body": ParagraphStyle("body", fontName="Helvetica", fontSize=10,
                textColor=TEXT_DARK, leading=16, alignment=TA_JUSTIFY, spaceAfter=6),
            "body_mid": ParagraphStyle("body_mid", fontName="Helvetica", fontSize=10,
                textColor=TEXT_MID, leading=15, spaceAfter=4),
            "label": ParagraphStyle("label", fontName="Helvetica-Bold", fontSize=9,
                textColor=TEXT_LIGHT, leading=12, spaceAfter=2),
            "bullet": ParagraphStyle("bullet", fontName="Helvetica", fontSize=10,
                textColor=TEXT_DARK, leading=15, leftIndent=16,
                bulletIndent=6, spaceAfter=4),
            "action_item": ParagraphStyle("action_item", fontName="Helvetica", fontSize=10,
                textColor=colors.HexColor("#065f46"), leading=15,
                leftIndent=16, bulletIndent=6, spaceAfter=4),
            "company_name": ParagraphStyle("company_name", fontName="Helvetica-Bold",
                fontSize=12, textColor=NAVY, leading=16),
            "small": ParagraphStyle("small", fontName="Helvetica", fontSize=8,
                textColor=TEXT_LIGHT, leading=11),
            "italic": ParagraphStyle("italic", fontName="Helvetica-Oblique", fontSize=10,
                textColor=ACCENT, leading=14),
            "toc_item": ParagraphStyle("toc_item", fontName="Helvetica", fontSize=10,
                textColor=TEXT_MID, leading=18, leftIndent=8),
            "highlight": ParagraphStyle("highlight", fontName="Helvetica-Bold", fontSize=10,
                textColor=colors.HexColor("#1e40af"), leading=15),
        }

    def _sig_color(self, sig: str) -> colors.Color:
        return {"high": HIGH_RED, "medium": MED_AMBER, "low": LOW_GREEN}.get(sig.lower(), TEXT_LIGHT)

    def _divider(self, color=ACCENT):
        return HRFlowable(width="100%", thickness=1, color=color, spaceAfter=10)

    def _section_title(self, text: str, icon: str = "") -> list:
        elements = []
        elements.append(Spacer(1, 0.3 * cm))
        elements.append(Paragraph(f"{icon} {text}".strip(), self.styles["section_header"]))
        elements.append(self._divider())
        return elements

    # ── COVER ────────────────────────────────────────────────────────────────

    def _build_cover(self, report: dict) -> list:
        elements = []
        title = report.get("report_title", "Weekly Competitive Intelligence Report")
        today = datetime.utcnow().strftime("%A, %B %d, %Y")
        companies = ", ".join(report.get("companies_analyzed", []))
        sources = report.get("data_sources_count", 0)

        cover_rows = [
            [Paragraph(title, self.styles["cover_title"])],
            [Paragraph(today, self.styles["cover_sub"])],
            [Spacer(1, 0.5 * cm)],
            [Paragraph(
                f"Tracking: {companies}   |   Sources analyzed: {sources}   |   Powered by Mistral AI + RAG",
                self.styles["cover_sub"]
            )],
        ]
        cover = Table(cover_rows, colWidths=[17 * cm])
        cover.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), NAVY),
            ("TOPPADDING", (0, 0), (-1, -1), 22),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 22),
            ("LEFTPADDING", (0, 0), (-1, -1), 28),
            ("RIGHTPADDING", (0, 0), (-1, -1), 28),
        ]))
        elements.append(cover)
        elements.append(Spacer(1, 0.3 * cm))

        # Confidence / quality bar
        meta = [[
            Paragraph("PRODUCTION RUN", ParagraphStyle("badge", fontName="Helvetica-Bold",
                fontSize=8, textColor=LOW_GREEN)),
            Paragraph(f"Generated: {today}", self.styles["label"]),
            Paragraph("Confidential — Internal Use Only", self.styles["label"]),
        ]]
        meta_t = Table(meta, colWidths=[4 * cm, 7 * cm, 6 * cm])
        meta_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ]))
        elements.append(meta_t)
        elements.append(Spacer(1, 0.4 * cm))

        # Table of contents
        toc_items = [
            "1.  Executive Summary",
            "2.  Key Developments This Week",
            "3.  Company-by-Company SWOT Analysis",
            "4.  Competitive Comparison & Positioning",
            "5.  Weak Signals & Early Threat Indicators",
            "6.  Strategic Recommendations to Outcompete",
            "7.  30-Day Outlook",
        ]
        toc_rows = [[Paragraph(item, self.styles["toc_item"])] for item in toc_items]
        toc_table = Table(toc_rows, colWidths=[17 * cm])
        toc_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 16),
            ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE, LIGHT_GRAY]),
        ]))
        elements.append(Paragraph("Contents", self.styles["subsection_header"]))
        elements.append(toc_table)
        elements.append(PageBreak())
        return elements

    # ── EXECUTIVE SUMMARY ────────────────────────────────────────────────────

    def _build_executive_summary(self, report: dict) -> list:
        elements = []
        elements += self._section_title("Executive Summary")
        summary = report.get("executive_summary", "No summary available.")
        elements.append(Paragraph(summary, self.styles["body"]))

        # Key numbers row
        companies = report.get("companies_analyzed", [])
        developments = report.get("key_developments", [])
        high_count = len([d for d in developments if d.get("significance") == "high"])
        signals = report.get("weak_signals", [])

        stats = [[
            Paragraph(f"{len(companies)}\nCompanies Tracked", ParagraphStyle("stat",
                fontName="Helvetica-Bold", fontSize=14, textColor=ACCENT,
                leading=18, alignment=TA_CENTER)),
            Paragraph(f"{len(developments)}\nDevelopments Found", ParagraphStyle("stat",
                fontName="Helvetica-Bold", fontSize=14, textColor=NAVY,
                leading=18, alignment=TA_CENTER)),
            Paragraph(f"{high_count}\nHigh Priority", ParagraphStyle("stat",
                fontName="Helvetica-Bold", fontSize=14, textColor=HIGH_RED,
                leading=18, alignment=TA_CENTER)),
            Paragraph(f"{len(signals)}\nWeak Signals", ParagraphStyle("stat",
                fontName="Helvetica-Bold", fontSize=14, textColor=MED_AMBER,
                leading=18, alignment=TA_CENTER)),
        ]]
        stats_t = Table(stats, colWidths=[4.25 * cm] * 4)
        stats_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
            ("TOPPADDING", (0, 0), (-1, -1), 14),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
            ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
            ("LINEBEFORE", (1, 0), (-1, -1), 0.5, BORDER),
        ]))
        elements.append(Spacer(1, 0.3 * cm))
        elements.append(stats_t)
        elements.append(Spacer(1, 0.4 * cm))
        return elements

    # ── KEY DEVELOPMENTS ─────────────────────────────────────────────────────

    def _build_key_developments(self, report: dict) -> list:
        elements = []
        elements += self._section_title("Key Developments This Week")
        developments = report.get("key_developments", [])

        if not developments:
            elements.append(Paragraph("No key developments recorded.", self.styles["body_mid"]))
            return elements

        # Sort: high first
        order = {"high": 0, "medium": 1, "low": 2}
        developments = sorted(developments, key=lambda x: order.get(x.get("significance", "low"), 2))

        for i, dev in enumerate(developments, 1):
            sig = dev.get("significance", "low")
            sig_color = self._sig_color(sig)

            header_data = [[
                Paragraph(f"{i}. {dev.get('company', '')}", self.styles["company_name"]),
                Paragraph(f"[ {sig.upper()} ]", ParagraphStyle("sig",
                    fontName="Helvetica-Bold", fontSize=9,
                    textColor=sig_color, alignment=TA_RIGHT)),
            ]]
            header_t = Table(header_data, colWidths=[12 * cm, 5 * cm])
            header_t.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]))

            title_text = dev.get("development", dev.get("title", ""))
            impl_text = dev.get("strategic_implication", "")
            category = dev.get("category", "general")

            card_content = [
                [header_t],
                [Paragraph(f"Category: {category.title()}", self.styles["small"])],
                [Spacer(1, 0.1 * cm)],
                [Paragraph(title_text, self.styles["body"])],
                [Paragraph(f"Strategic Implication: {impl_text}",
                    self.styles["italic"])],
            ]
            card = Table(card_content, colWidths=[17 * cm])
            card.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
                ("BACKGROUND", (0, 0), (-1, 0), WHITE),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 14),
                ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
                ("LINEBELOW", (0, 0), (-1, 0), 1, sig_color),
            ]))
            elements.append(KeepTogether([card, Spacer(1, 0.25 * cm)]))

        elements.append(Spacer(1, 0.3 * cm))
        return elements

    # ── SWOT PER COMPANY ─────────────────────────────────────────────────────

    def _build_swot_detailed(self, report: dict, analyses: list) -> list:
        elements = []
        elements += self._section_title("Company-by-Company SWOT Analysis")

        if not analyses:
            # Fall back to swot_summary if detailed analyses not available
            swot_data = report.get("swot_summary", [])
            for item in swot_data:
                elements.append(Paragraph(item.get("company", ""), self.styles["subsection_header"]))
                elements.append(Paragraph(f"Strength: {item.get('top_strength', '—')}", self.styles["body"]))
                elements.append(Paragraph(f"Threat: {item.get('top_threat', '—')}", self.styles["body"]))
            return elements

        for analysis in analyses:
            if analysis.get("error"):
                continue
            company = analysis.get("company", "Unknown")
            swot = analysis.get("swot", {})

            elements.append(Paragraph(company, self.styles["subsection_header"]))

            swot_rows = [
                [
                    Paragraph("STRENGTHS", ParagraphStyle("sw_h", fontName="Helvetica-Bold",
                        fontSize=9, textColor=WHITE)),
                    Paragraph("WEAKNESSES", ParagraphStyle("sw_h", fontName="Helvetica-Bold",
                        fontSize=9, textColor=WHITE)),
                    Paragraph("OPPORTUNITIES", ParagraphStyle("sw_h", fontName="Helvetica-Bold",
                        fontSize=9, textColor=WHITE)),
                    Paragraph("THREATS", ParagraphStyle("sw_h", fontName="Helvetica-Bold",
                        fontSize=9, textColor=WHITE)),
                ]
            ]

            strengths = swot.get("strengths", [])
            weaknesses = swot.get("weaknesses", [])
            opportunities = swot.get("opportunities", [])
            threats = swot.get("threats", [])
            max_rows = max(len(strengths), len(weaknesses), len(opportunities), len(threats), 1)

            for j in range(max_rows):
                row = [
                    Paragraph(f"• {strengths[j]}" if j < len(strengths) else "", self.styles["bullet"]),
                    Paragraph(f"• {weaknesses[j]}" if j < len(weaknesses) else "", self.styles["bullet"]),
                    Paragraph(f"• {opportunities[j]}" if j < len(opportunities) else "", self.styles["bullet"]),
                    Paragraph(f"• {threats[j]}" if j < len(threats) else "", self.styles["bullet"]),
                ]
                swot_rows.append(row)

            swot_t = Table(swot_rows, colWidths=[4.25 * cm] * 4)
            swot_t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (0, 0), LOW_GREEN),
                ("BACKGROUND", (1, 0), (1, 0), HIGH_RED),
                ("BACKGROUND", (2, 0), (2, 0), ACCENT),
                ("BACKGROUND", (3, 0), (3, 0), MED_AMBER),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]))
            elements.append(swot_t)

            # Strategic themes
            themes = analysis.get("strategic_themes", [])
            if themes:
                elements.append(Spacer(1, 0.2 * cm))
                theme_text = "  |  ".join(themes)
                elements.append(Paragraph(f"Strategic themes: {theme_text}", self.styles["small"]))

            elements.append(Spacer(1, 0.4 * cm))

        return elements

    # ── COMPETITIVE COMPARISON ───────────────────────────────────────────────

    def _build_comparison(self, report: dict) -> list:
        elements = []
        elements += self._section_title("Competitive Comparison & Positioning")

        comp = report.get("competitive_comparison", {})
        if not comp:
            return elements

        rows = [
            [Paragraph("Most Active Company", self.styles["label"]),
             Paragraph(comp.get("most_active_company", "—"), self.styles["body"])],
            [Paragraph("Reason", self.styles["label"]),
             Paragraph(comp.get("most_active_reason", "—"), self.styles["body"])],
            [Paragraph("Biggest Threat", self.styles["label"]),
             Paragraph(comp.get("biggest_threat", "—"), self.styles["body"])],
            [Paragraph("Biggest Opportunity", self.styles["label"]),
             Paragraph(comp.get("biggest_opportunity", "—"), self.styles["body"])],
        ]
        t = Table(rows, colWidths=[5 * cm, 12 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), LIGHT_BLUE),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 0.4 * cm))
        return elements

    # ── WEAK SIGNALS ─────────────────────────────────────────────────────────

    def _build_weak_signals(self, report: dict) -> list:
        elements = []
        elements += self._section_title("Weak Signals & Early Threat Indicators")

        signals = report.get("weak_signals", [])
        if not signals:
            elements.append(Paragraph("No weak signals detected this week.", self.styles["body_mid"]))
            return elements

        for sig in signals:
            velocity = sig.get("velocity_score", 0)
            strength_label = "STRONG" if velocity > 5 else "MODERATE" if velocity > 2 else "WEAK"
            strength_color = HIGH_RED if velocity > 5 else MED_AMBER if velocity > 2 else LOW_GREEN

            content = [
                [Paragraph(f"Signal: {sig.get('signal', '')}", self.styles["highlight"]),
                 Paragraph(strength_label, ParagraphStyle("str", fontName="Helvetica-Bold",
                    fontSize=9, textColor=strength_color, alignment=TA_RIGHT))],
                [Paragraph(f"Companies involved: {sig.get('company', '—')}", self.styles["small"]),
                 Paragraph(f"Velocity score: {velocity:.1f}", self.styles["small"])],
                [Paragraph(f"Recommended action: {sig.get('recommended_action', '')}",
                    self.styles["italic"]), Paragraph("", self.styles["small"])],
            ]
            card = Table(content, colWidths=[13 * cm, 4 * cm])
            card.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fffbeb")),
                ("BOX", (0, 0), (-1, -1), 1, MED_AMBER),
                ("LINEBELOW", (0, 0), (-1, 0), 0.5, BORDER),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("SPAN", (0, 2), (1, 2)),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            elements.append(KeepTogether([card, Spacer(1, 0.2 * cm)]))

        elements.append(Spacer(1, 0.3 * cm))
        return elements

    # ── STRATEGIC RECOMMENDATIONS ────────────────────────────────────────────

    def _build_recommendations(self, report: dict, analyses: list) -> list:
        elements = []
        elements += self._section_title("Strategic Recommendations to Outcompete")

        elements.append(Paragraph(
            "Based on this week's intelligence, here are concrete actions your organization "
            "should take to gain competitive advantage:",
            self.styles["body"]
        ))
        elements.append(Spacer(1, 0.2 * cm))

        developments = report.get("key_developments", [])
        companies = report.get("companies_analyzed", [])

        # Generate recommendations from analysis data
        recs = []

        # From competitive comparison
        comp = report.get("competitive_comparison", {})
        most_active = comp.get("most_active_company", "")
        if most_active:
            recs.append({
                "priority": "IMMEDIATE",
                "color": HIGH_RED,
                "title": f"Counter {most_active}'s Market Activity",
                "action": (
                    f"{most_active} is the most active competitor this week. "
                    f"Reason: {comp.get('most_active_reason', '')}. "
                    f"Recommended counter: Accelerate your own product announcements or pricing responses "
                    f"within the next 7 days to avoid ceding market perception to {most_active}."
                ),
            })

        # From biggest threat
        threat = comp.get("biggest_threat", "")
        if threat:
            recs.append({
                "priority": "HIGH",
                "color": MED_AMBER,
                "title": "Address the Primary Competitive Threat",
                "action": (
                    f"The biggest threat identified this week: {threat}. "
                    f"Action: Conduct an internal review of your product roadmap against this threat. "
                    f"Identify 2-3 features or capabilities you can ship or announce within 30 days "
                    f"to directly address this competitive pressure."
                ),
            })

        # From biggest opportunity
        opp = comp.get("biggest_opportunity", "")
        if opp:
            recs.append({
                "priority": "HIGH",
                "color": TEAL,
                "title": "Capitalize on the Market Opportunity",
                "action": (
                    f"Key opportunity identified: {opp}. "
                    f"Action: Assign a dedicated team to evaluate how your organization can enter or "
                    f"strengthen its position in this opportunity within the next sprint cycle."
                ),
            })

        # From SWOT weaknesses of competitors
        for analysis in analyses:
            if analysis.get("error"):
                continue
            company = analysis.get("company", "")
            weaknesses = analysis.get("swot", {}).get("weaknesses", [])
            if weaknesses:
                recs.append({
                    "priority": "MEDIUM",
                    "color": ACCENT,
                    "title": f"Exploit {company}'s Weaknesses",
                    "action": (
                        f"{company} key weakness: {weaknesses[0]}. "
                        f"Action: Position your product or messaging directly against this gap. "
                        f"Update your sales battlecards and marketing material to highlight your "
                        f"advantage where {company} is weakest."
                    ),
                })

        # From weak signals
        for sig in report.get("weak_signals", [])[:2]:
            recs.append({
                "priority": "MONITOR",
                "color": PURPLE,
                "title": f"Monitor: {sig.get('signal', 'Emerging signal')}",
                "action": (
                    f"This signal is accelerating across {sig.get('company', 'multiple competitors')}. "
                    f"Set up a weekly tracking dashboard for this topic. "
                    f"If velocity increases further, escalate to a strategic response."
                ),
            })

        # Render each recommendation
        for i, rec in enumerate(recs, 1):
            priority_color = rec["color"]
            rows = [
                [
                    Paragraph(f"{i}. {rec['title']}", self.styles["company_name"]),
                    Paragraph(rec["priority"], ParagraphStyle("pri", fontName="Helvetica-Bold",
                        fontSize=8, textColor=priority_color, alignment=TA_RIGHT)),
                ],
                [Paragraph(rec["action"], self.styles["action_item"]),
                 Paragraph("", self.styles["small"])],
            ]
            card = Table(rows, colWidths=[13 * cm, 4 * cm])
            card.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f0fdf4")),
                ("BOX", (0, 0), (-1, -1), 0.5, priority_color),
                ("LINEBELOW", (0, 0), (-1, 0), 0.5, BORDER),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("LEFTPADDING", (0, 0), (-1, -1), 14),
                ("SPAN", (0, 1), (1, 1)),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            elements.append(KeepTogether([card, Spacer(1, 0.2 * cm)]))

        elements.append(Spacer(1, 0.3 * cm))
        return elements

    # ── OUTLOOK ──────────────────────────────────────────────────────────────

    def _build_outlook(self, report: dict) -> list:
        elements = []
        elements.append(PageBreak())
        elements += self._section_title("30-Day Outlook")
        outlook = report.get("outlook_30_days", "Outlook unavailable.")
        if not outlook or outlook.strip() == "":
            outlook = "Synthetic data indicates continued market shifts across all tracked companies in the next 30 days."
        elements.append(Paragraph(outlook.strip(), self.styles["body"]))

        # Footer
        elements.append(Spacer(1, 1 * cm))
        elements.append(self._divider(BORDER))
        footer_text = (
            f"Report generated: {datetime.utcnow().strftime('%B %d, %Y at %H:%M UTC')}  |  "
            f"System: Multi-Agent Competitive Intelligence  |  "
            f"LLM: Mistral AI  |  RAG: Qdrant Vector DB  |  "
            f"Confidential — Internal Use Only"
        )
        elements.append(Paragraph(footer_text, self.styles["small"]))
        return elements

    # ── MAIN RENDER ──────────────────────────────────────────────────────────

    def render(self, report_data: dict, analyses: list = None) -> Path:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filepath = self.output_dir / f"competitive_report_{timestamp}.pdf"

        doc = SimpleDocTemplate(
            str(filepath), pagesize=A4,
            leftMargin=2 * cm, rightMargin=2 * cm,
            topMargin=2 * cm, bottomMargin=2 * cm,
        )

        analyses = analyses or []

        elements = []
        elements += self._build_cover(report_data)
        elements += self._build_executive_summary(report_data)
        elements += self._build_key_developments(report_data)
        elements += self._build_swot_detailed(report_data, analyses)
        elements += self._build_comparison(report_data)
        elements += self._build_weak_signals(report_data)
        elements += self._build_recommendations(report_data, analyses)
        elements += self._build_outlook(report_data)

        doc.build(elements)
        logger.info(f"[PDF] Report saved to: {filepath}")
        return filepath
