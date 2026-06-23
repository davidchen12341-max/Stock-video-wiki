#!/usr/bin/env python3
"""
Generate a PDF brief from the stock YouTuber wiki.
Covers all channels except Tyler Hill.
Output: wiki/weekly-brief-<date>.pdf
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from datetime import date

OUTPUT = "/Users/davidchen/Desktop/build-wiki/wiki/stock-channels-brief-june-2026.pdf"
TODAY = date.today().strftime("%B %d, %Y")

# ── Styles ────────────────────────────────────────────────────────────────────

def build_styles():
    base = getSampleStyleSheet()
    s = {}

    s["cover_title"] = ParagraphStyle(
        "cover_title", parent=base["Title"],
        fontSize=28, textColor=colors.HexColor("#0D1B2A"),
        spaceAfter=8, alignment=TA_CENTER, leading=34
    )
    s["cover_sub"] = ParagraphStyle(
        "cover_sub", parent=base["Normal"],
        fontSize=13, textColor=colors.HexColor("#4A6FA5"),
        spaceAfter=4, alignment=TA_CENTER, leading=18
    )
    s["cover_date"] = ParagraphStyle(
        "cover_date", parent=base["Normal"],
        fontSize=11, textColor=colors.HexColor("#888888"),
        spaceAfter=0, alignment=TA_CENTER
    )
    s["h1"] = ParagraphStyle(
        "h1", parent=base["Heading1"],
        fontSize=18, textColor=colors.HexColor("#0D1B2A"),
        spaceBefore=18, spaceAfter=6, leading=24
    )
    s["h2"] = ParagraphStyle(
        "h2", parent=base["Heading2"],
        fontSize=13, textColor=colors.HexColor("#4A6FA5"),
        spaceBefore=12, spaceAfter=4, leading=18
    )
    s["h3"] = ParagraphStyle(
        "h3", parent=base["Heading3"],
        fontSize=11, textColor=colors.HexColor("#1A3A5C"),
        spaceBefore=8, spaceAfter=2, leading=15
    )
    s["body"] = ParagraphStyle(
        "body", parent=base["Normal"],
        fontSize=10, textColor=colors.HexColor("#222222"),
        spaceAfter=5, leading=15, alignment=TA_JUSTIFY
    )
    s["bullet"] = ParagraphStyle(
        "bullet", parent=base["Normal"],
        fontSize=10, textColor=colors.HexColor("#222222"),
        spaceAfter=3, leading=14, leftIndent=14, bulletIndent=0,
        bulletFontName="Helvetica", bulletFontSize=10
    )
    s["ticker_label"] = ParagraphStyle(
        "ticker_label", parent=base["Normal"],
        fontSize=9, textColor=colors.HexColor("#FFFFFF"),
        leading=12
    )
    s["callout"] = ParagraphStyle(
        "callout", parent=base["Normal"],
        fontSize=10, textColor=colors.HexColor("#0D1B2A"),
        backColor=colors.HexColor("#EEF4FB"),
        spaceAfter=4, leading=14, leftIndent=10, rightIndent=10,
        borderPad=6
    )
    s["caption"] = ParagraphStyle(
        "caption", parent=base["Normal"],
        fontSize=8, textColor=colors.HexColor("#777777"),
        spaceAfter=2, leading=11, alignment=TA_CENTER
    )
    s["disclaimer"] = ParagraphStyle(
        "disclaimer", parent=base["Normal"],
        fontSize=8, textColor=colors.HexColor("#999999"),
        spaceAfter=2, leading=11, alignment=TA_CENTER
    )
    return s


def hr(color="#CCCCCC", thickness=0.5):
    return HRFlowable(width="100%", thickness=thickness,
                      color=colors.HexColor(color), spaceAfter=6, spaceBefore=2)


def bullet(text, style):
    return Paragraph(f"• {text}", style)


def tag_table(tickers, color_hex="#4A6FA5"):
    """Render a compact row of ticker chips."""
    if not tickers:
        return None
    chips = []
    for t in tickers:
        chip = Table(
            [[Paragraph(f"<b>{t}</b>", ParagraphStyle(
                "chip", fontSize=8, textColor=colors.white, leading=10))]],
            colWidths=[len(t) * 7 + 10]
        )
        chip.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(color_hex)),
            ("ROUNDEDCORNERS", [3]),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ]))
        chips.append(chip)
    # wrap in a single-row table
    if len(chips) > 1:
        row_table = Table([chips], hAlign="LEFT")
        row_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 2),
            ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ]))
        return row_table
    return chips[0]


# ── Content sections ───────────────────────────────────────────────────────────

def cover_page(s):
    elems = []
    elems.append(Spacer(1, 1.6 * inch))
    elems.append(Paragraph("Stock YouTubers", s["cover_sub"]))
    elems.append(Paragraph("Channel Brief", s["cover_title"]))
    elems.append(Spacer(1, 0.1 * inch))
    elems.append(hr("#4A6FA5", 1.5))
    elems.append(Spacer(1, 0.1 * inch))
    elems.append(Paragraph("Key Themes · Stock Ideas · Notable Calls", s["cover_sub"]))
    elems.append(Spacer(1, 0.25 * inch))
    elems.append(Paragraph(f"Compiled {TODAY}  ·  Sources: May 27 – June 23, 2026", s["cover_date"]))
    elems.append(Paragraph("Channels: ZipTrader · Felix Friends · Wallstreet Trapper · Nolan Gouveia", s["cover_date"]))
    elems.append(Spacer(1, 2 * inch))
    elems.append(Paragraph(
        "This document summarizes publicly available YouTube content for informational purposes only. "
        "Nothing here is financial advice. Always do your own research.",
        s["disclaimer"]
    ))
    elems.append(PageBreak())
    return elems


def toc_page(s):
    elems = []
    elems.append(Paragraph("Contents", s["h1"]))
    elems.append(hr())
    sections = [
        ("1", "Executive Summary", "Big picture: what the channels agreed and disagreed on"),
        ("2", "Macro & Market Themes", "SpaceX IPO, AI supercycle, financial repression, sector rotation"),
        ("3", "Stock Ideas by Category", "Semis · Space · AI Infrastructure · Biotech · Software · ETFs"),
        ("4", "Channel-by-Channel Breakdown", "ZipTrader · Felix Friends · Wallstreet Trapper · Nolan Gouveia"),
        ("5", "Watchlist & Catalyst Calendar", "Key dates and catalysts to monitor"),
    ]
    for num, title, desc in sections:
        elems.append(Spacer(1, 4))
        row = Table(
            [[Paragraph(f"<b>{num}.</b>", s["body"]),
              Paragraph(f"<b>{title}</b>", s["body"]),
              Paragraph(desc, ParagraphStyle("toc_desc", parent=s["body"],
                                             textColor=colors.HexColor("#666666")))
              ]],
            colWidths=[0.35 * inch, 2.2 * inch, 4.0 * inch]
        )
        row.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elems.append(row)
    elems.append(PageBreak())
    return elems


def section_executive_summary(s):
    elems = []
    elems.append(Paragraph("1. Executive Summary", s["h1"]))
    elems.append(hr())
    elems.append(Paragraph(
        "Across roughly 30 videos published between late May and late June 2026, four channels covering very "
        "different investing styles converged on a few shared beliefs — and diverged sharply on others.",
        s["body"]
    ))
    elems.append(Spacer(1, 6))

    elems.append(Paragraph("Where they agreed", s["h2"]))
    agrees = [
        "AI infrastructure is a decade-long supercycle — data centers, memory, and power are the bottleneck, not chips alone.",
        "The SpaceX IPO at its opening valuation (~$1.75–2.8T) is too expensive to buy outright; the real play is the ecosystem around it.",
        "The stock market is broadly in a bull phase and pulling back is a buying opportunity, not a reason to exit.",
        "Biotech and neglected sectors are offering the best value in a market where AI/chip stocks have crowded out everything else.",
        "Financial repression is real — holding cash long-term destroys purchasing power at roughly -2.4% real yield.",
    ]
    for a in agrees:
        elems.append(bullet(a, s["bullet"]))
    elems.append(Spacer(1, 6))

    elems.append(Paragraph("Key divergences", s["h2"]))
    divs = [
        "ZipTrader and Felix Friends focused heavily on individual stock picks; Wallstreet Trapper emphasized ETFs, mindset, and options strategy.",
        "Wallstreet Trapper prefers ETFs (QTUM, CQTM, UFO) for space/quantum exposure; ZipTrader and Felix went name-by-name (GSAT, ASTS, RGTI, IONQ).",
        "Felix Friends turned notably bearish on S&P 500 index funds mid-June, warning of $350B in forced selling from mega-IPOs; Trapper stayed broadly bullish.",
        "Nolan Gouveia operates in a different lane entirely — passive income and account placement optimization, not growth picks.",
    ]
    for d in divs:
        elems.append(bullet(d, s["bullet"]))
    elems.append(Spacer(1, 8))

    elems.append(Paragraph("Most frequently mentioned tickers (across all channels)", s["h2"]))
    tickers_data = [
        ["Ticker", "Channels", "Consensus View"],
        ["MU (Micron)", "ZipTrader, W.Trapper", "AI memory bottleneck; bull — 2–3 more years of runway"],
        ["NVDA", "All channels", "Foundation; hold; overowned but thesis intact"],
        ["RGTI (Rigetti)", "ZipTrader, Felix", "Quantum pure-play; high risk; $100M CHIPS LOI catalyst"],
        ["NOW (ServiceNow)", "ZipTrader, Felix, W.Trapper", "Mixed — Felix/ZIP bullish; Trapper sees AI headwinds"],
        ["ASTS", "ZipTrader, W.Trapper", "SpaceX ecosystem; watchlist; regulatory risk flagged"],
        ["RDW (Redwire)", "ZipTrader, Felix", "Space/defense components; +163–193% from prior calls"],
        ["BEAM", "ZipTrader", "Biotech compounder; 72% off ATH; first in-vivo human data"],
        ["GSAT", "ZipTrader", "SpaceX acquisition candidate #1; spectrum play"],
        ["SCHD", "Nolan, W.Trapper", "Core dividend ETF; holds in any account; 11.6% div CAGR"],
    ]
    t = Table(tickers_data, colWidths=[1.15 * inch, 1.7 * inch, 3.7 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0D1B2A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.HexColor("#F7F9FC"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elems.append(t)
    elems.append(PageBreak())
    return elems


def section_macro(s):
    elems = []
    elems.append(Paragraph("2. Macro & Market Themes", s["h1"]))
    elems.append(hr())

    elems.append(Paragraph("The AI Supercycle", s["h2"]))
    elems.append(Paragraph(
        "Wallstreet Trapper made the most explicit call: AI is a 10-year structural supercycle comparable to "
        "the industrial revolution. Semiconductors reached ~15% of S&P 500 weight by 2025 — the largest "
        "sector. Big tech is spending $630B on data center capex in 2026 alone, with the industry growing to "
        "$1.1T by 2035. Trapper's bottleneck framework: <b>the constraint is memory and power, not chips.</b> "
        "MU, STX, and WDC are the memory plays; VRT and FLNC are the power plays.",
        s["body"]
    ))
    elems.append(Spacer(1, 4))

    elems.append(Paragraph("The SpaceX IPO — Agreed: Don't Buy the IPO", s["h2"]))
    elems.append(Paragraph(
        "All three growth-focused channels covered the SpaceX IPO (priced at $135, ran to ~$213 at time of "
        "ZipTrader's June 17 video, implying ~$2.8T market cap). The consensus: the opening valuation is "
        "irrational given a 4% float, forced index buying, and IPO euphoria. Dec 8, 2026 is the key date — "
        "the 180-day lockup expiry — which ZipTrader called 'a candidate for one of the largest single-day "
        "insider selling events in market history.' Elon's personal shares unlock June 12, 2027.",
        s["body"]
    ))
    elems.append(Spacer(1, 4))
    spacex_table = [
        ["Channel", "SpaceX View", "Alternative Play"],
        ["ZipTrader", "Don't buy at $213; wait for lockup selloff; target below $1.5T", "GSAT, SATS, VSAT, ASTS, RDW, PL, SPIR, LUNR"],
        ["Felix Friends", "Structurally bullish long-term ($10T company thesis) but index fund forced-selling risk is the near-term danger", "Audit 401k concentration; rotate to basic materials"],
        ["Wallstreet Trapper", "100x revenue = trap; IPO pattern is run-up then dump at lockup expiry; wait 2+ years for earnings", "UFO, NASA, MARS space ETFs; ASTS, RKLB watchlist"],
    ]
    t = Table(spacex_table, colWidths=[1.2 * inch, 2.5 * inch, 2.85 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A3A5C")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F0F5FB"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elems.append(t)
    elems.append(Spacer(1, 8))

    elems.append(Paragraph("Quantum Computing — The Next Government-Backed Wave", s["h2"]))
    elems.append(Paragraph(
        "Both Wallstreet Trapper and ZipTrader flagged quantum computing as an early-stage sector with government "
        "validation. The Trump administration's $2.013B CHIPS Act quantum funding (9 letters of intent) was the "
        "catalyst. Trapper's play: quantum ETFs (QTUM, CQTM) to avoid picking the winner. ZipTrader's play: "
        "INFQ (Infleqtion) as the highest-conviction pure-play with 5 specific catalysts. Felix separately "
        "flagged RGTI, QBTS, and IONQ as 10-bagger candidates in the $1–10B market cap sweet spot.",
        s["body"]
    ))
    elems.append(Spacer(1, 4))

    elems.append(Paragraph("Financial Repression (Nolan Gouveia)", s["h2"]))
    elems.append(Paragraph(
        "Nolan Gouveia provided the macro macro context: US debt-to-GDP at ~100% (matching 1946 levels) means "
        "the government is structurally motivated to hold real rates below inflation. With the Fed funds rate "
        "at 3.5–3.75% and CPI at 3.8%, cash in a regular savings account (0.45% APY) earns a real yield of "
        "<b>-2.4%</b>. The defense: a three-move ETF portfolio (60% SCHD/VYM/VOO, 25% TIPS ladder, 15% HYSA "
        "buffer) projects to $122K real value over 10 years vs. $78K in a savings account — a $44K gap on $100K.",
        s["body"]
    ))
    elems.append(Spacer(1, 4))

    elems.append(Paragraph("Felix Friends — Bearish on S&P 500 Concentration (June 9)", s["h2"]))
    elems.append(Paragraph(
        "Felix's most bearish macro call of the period: three mega-IPOs (SpaceX, OpenAI, Anthropic at $60–75B "
        "each) plus Google printing $85B in shares creates ~$350B in forced selling pressure on S&P 500 "
        "index funds. The Nasdaq 15-day fast-entry rule means passive funds must sell existing holdings to "
        "buy the new entrants. Felix's three-step action: audit 401k concentration using the 0.4 multiplier, "
        "track smart money rotation into basic materials, and build watchlists before the dip.",
        s["body"]
    ))
    elems.append(PageBreak())
    return elems


def section_stock_ideas(s):
    elems = []
    elems.append(Paragraph("3. Stock Ideas by Category", s["h1"]))
    elems.append(hr())

    # ── AI Memory & Semiconductors ──
    elems.append(Paragraph("AI Memory & Semiconductors", s["h2"]))
    elems.append(Paragraph(
        "The most consistently bullish consensus trade across all growth channels. "
        "Trapper's bottleneck framework puts memory as the single most critical AI supply constraint.",
        s["body"]
    ))
    mem_data = [
        ["Ticker", "Price Context", "Thesis", "Risk"],
        ["MU\n(Micron)", "+139% YTD at time of coverage;\n$47K options profit for Trapper",
         "AI needs HBM and fast DRAM; MU is the US-listed supplier with the most upside; Trapper: '2–3 more years of runway'",
         "Cyclical; macro slowdown would hit orders"],
        ["STX\n(Seagate)", "Held at technical support after dip;\nFreedom Index holding",
         "Storage bottleneck for AI training data; Trapper held through community panic",
         "Commodity-ish pricing"],
        ["WDC/SNDK\n(SanDisk)", "+462% YTD on hedge fund most-loved list",
         "Pivoted to AI memory; highest-returning name on Trapper's hedge fund data screen",
         "Already ran hard — late entry risk"],
        ["MRVL\n(Marvell)", "ZipTrader setup (June 8)",
         "Custom AI silicon, data center interconnects; ZipTrader called it a setup alongside MU",
         "Competes with NVDA in custom ASIC space"],
    ]
    t = Table(mem_data, colWidths=[0.85 * inch, 1.45 * inch, 2.65 * inch, 1.6 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0D1B2A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F7F9FC"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    elems.append(t)
    elems.append(Spacer(1, 10))

    # ── Space & SpaceX Ecosystem ──
    elems.append(Paragraph("Space & SpaceX Ecosystem", s["h2"]))
    elems.append(Paragraph(
        "The SpaceX IPO dominated space coverage. ZipTrader's June 17 video is the most detailed breakdown: "
        "avoid SpaceX at $213 but position in its likely acquisition targets and supply chain partners.",
        s["body"]
    ))
    space_data = [
        ["Ticker", "Angle", "Channel", "Priority"],
        ["GSAT", "Spectrum + iPhone SOS; SpaceX acquisition #1", "ZipTrader", "High"],
        ["SATS (EchoStar)", "Already partial SpaceX spectrum deal; could be fully acquired", "ZipTrader", "High"],
        ["VSAT (Viasat)", "Large global spectrum stockpile; acquisition candidate", "ZipTrader", "Medium"],
        ["ASTS (AST SpaceMobile)", "SpaceX's phone-to-satellite competitor; boldest idea; regulatory risk", "ZipTrader, W.Trapper", "Speculative"],
        ["RDW (Redwire)", "Spacecraft components; supply chain bolt-on; +163–193% from prior calls", "ZipTrader, Felix", "Medium"],
        ["LUNR (Intuitive Machines)", "Moon landers; fits SpaceX lunar/Mars roadmap", "ZipTrader", "Speculative"],
        ["PL (Planet Labs)", "Space data for defense/government; SpaceX data partner", "ZipTrader, W.Trapper", "Medium"],
        ["RKLB (Rocket Lab)", "Flagged by W.Trapper as 'coming soon' watchlist entry", "W.Trapper", "Watchlist"],
        ["UFO / MARS ETF", "Space ETF — owns SpaceX automatically post-inclusion", "W.Trapper", "Low risk"],
    ]
    t = Table(space_data, colWidths=[1.15 * inch, 2.7 * inch, 1.45 * inch, 1.25 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A3A5C")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F0F5FB"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    elems.append(t)
    elems.append(Spacer(1, 10))

    # ── Quantum ──
    elems.append(Paragraph("Quantum Computing", s["h2"]))
    quantum_data = [
        ["Ticker", "Angle", "Channel", "Key Catalyst"],
        ["RGTI (Rigetti)", "$100M CHIPS Act LOI + Lyra chip H2 2026 + NVDA integration; +1,000% prior call", "ZipTrader, Felix", "Lyra chip shipments; LOI → deal (Jul–Sep 2026)"],
        ["QBTS (D-Wave)", "$100M CHIPS Act LOI; most commercially deployed quantum company", "ZipTrader, Felix", "Revenue growth; commercial quantum adoption"],
        ["IONQ", "+329% profit growth last quarter; strongest momentum metric; didn't get CHIPS funding (too much cash)", "ZipTrader, Felix", "Q2/Q3 earnings; commercial contracts"],
        ["INFQ (Infleqtion)", "ZipTrader's #1 quantum pick; 12 logical qubits vs 1-2 industry avg; $40M 2026 revenue guide", "ZipTrader", "30 qubits milestone Q4 2026; CHIPS final deal"],
        ["QTUM / CQTM ETF", "Quantum ETF basket — own the infrastructure without picking the winner", "W.Trapper", "Government quantum spending trajectory"],
    ]
    t = Table(quantum_data, colWidths=[1.15 * inch, 2.35 * inch, 1.2 * inch, 1.85 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0D1B2A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F7F9FC"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    elems.append(t)
    elems.append(Spacer(1, 10))

    # ── AI Infrastructure & Power ──
    elems.append(Paragraph("AI Infrastructure & Power", s["h2"]))
    infra_data = [
        ["Ticker", "Angle", "Notable Numbers"],
        ["VRT (Vertiv)", "Data center cooling and power distribution; Felix's 'what Cisco was to the internet'", "Profitable + FCF; at/near ATH; customers: MSFT, AMZN, GOOGL, META"],
        ["FLNC (Fluence Energy)", "Grid-scale battery storage = speed-to-power for AI data centers; deploy in months vs years on utility grid", "$5.6B backlog; Siemens + NVDA joint deal; +50% day after ZipTrader coverage"],
        ["VICR (Vicor)", "Power conversion chips that convert wall power to precise GPU voltage; every AI chip needs one", "Profitable today; revenue guidance raised; new licensing deal; near ATH"],
        ["NNE (NaNuclear)", "Nuclear fuel logistics — the 'railway in the gold rush'; acquired Secure Transportation Services for $13M", "$550M cash, zero revenue; Felix's chart shows basing pattern; watch for breakout"],
        ["OKLO", "DOE surplus plutonium program (free fuel); Meta, Nvidia, Equinix customers", "$2.5B cash; test reactor July 2026; commercial 2032–33"],
    ]
    t = Table(infra_data, colWidths=[1.05 * inch, 2.8 * inch, 2.7 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A3A5C")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F0F5FB"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    elems.append(t)
    elems.append(Spacer(1, 10))

    # ── Biotech ──
    elems.append(Paragraph("Biotech — The Value Pocket", s["h2"]))
    elems.append(Paragraph(
        "The most bullish biotech calls across the period. ZipTrader's BEAM thesis and Felix's ADPT thesis "
        "share a common structure: great science or growing business, stock deeply discounted from highs, "
        "specific near-term catalyst that could force a re-rating.",
        s["body"]
    ))
    bio_data = [
        ["Ticker", "Price / Discount", "Thesis & Catalyst", "Risk"],
        ["BEAM\n(Beam Therapeutics)", "~$35; 72% off ATH;\n~$3.4B mkt cap",
         "First-ever in-vivo base-editing correction in a human (March 2025). Partners: Pfizer, Eli Lilly ($200M+), Apellis. BEAM-302 AATD data 2H 2026 (±20–35% expected move).",
         "Cash runway to 2027 only; dilution risk; binary clinical outcomes"],
        ["ADPT\n(Adaptive Bio)", "~87% off 2021 peak;\n$2.7B mkt cap",
         "ClonoSEQ is the only FDA-cleared MRD test; 50%+ of US blood cancer docs ordering; revenue +102%, +51%, +35% over 3 quarters. Profitability inflection is the catalyst.",
         "Felix's highest-risk biotech call; 87% drawdown means conviction requires evidence"],
        ["CMPS\n(Compass Pathways)", "Speculative;  binary",
         "FDA psilocybin approval as a binary mental health drug class catalyst",
         "Pre-revenue; binary FDA outcome; highest risk in Felix's 10-bagger list"],
    ]
    t = Table(bio_data, colWidths=[1.05 * inch, 1.3 * inch, 3.0 * inch, 1.2 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0D1B2A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F7F9FC"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    elems.append(t)
    elems.append(Spacer(1, 10))

    # ── Software / SaaS ──
    elems.append(Paragraph("Software / SaaS", s["h2"]))
    saas_data = [
        ["Ticker", "Channel", "Bull Case", "Bear Case"],
        ["NOW\n(ServiceNow)", "ZipTrader, Felix,\nW.Trapper (cautious)",
         "AI becomes its platform; 6 politicians + CEO buying; $5B buyback; NOW Assist $0→$750M in one year",
         "W.Trapper: Anthropic punched enterprise software in the face"],
        ["HIMS\n(Hims & Hers)", "ZipTrader",
         "2.6M subscribers, +59% revenue, $1.72B short interest, FDA peptide decision July 2026",
         "Earnings quarter was rough; 57% off highs"],
        ["ZETA\n(Zeta Global)", "ZipTrader",
         "19 consecutive beat-and-raise quarters; AI marketing automation +700% workflows; first GAAP net income 2026",
         "High valuation on a forward basis; reliant on continued AI marketing adoption"],
        ["ORCL\n(Oracle)", "Felix",
         "$500B backlog; $90B revenue guided FY2026; $1B buyback; Larry Ellison AI cloud bet",
         "Dependent on OpenAI/Anthropic paying their cloud bills"],
        ["BBAI\n(BigBear.AI)", "ZipTrader, Felix",
         "Defense AI contracts; +98% profit growth; $58 2031 bull case from ZipTrader",
         "Pre-scaled revenue; high customer concentration in government"],
    ]
    t = Table(saas_data, colWidths=[1.0 * inch, 1.2 * inch, 2.65 * inch, 1.7 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A3A5C")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F0F5FB"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    elems.append(t)
    elems.append(Spacer(1, 10))

    # ── ETFs & Passive ──
    elems.append(Paragraph("ETFs & Passive Income (Nolan Gouveia + W.Trapper)", s["h2"]))
    etf_data = [
        ["ETF", "Category", "Best Account Placement", "Key Stats"],
        ["SCHD", "Dividend growth", "Any — most tax-flexible", "11.6% dividend CAGR; 3.3% current yield"],
        ["JEPI / JEPQ", "Covered-call income", "Tax-advantaged only (IRA/Roth)", "High ordinary income = taxable brokerage trap"],
        ["SPYI / QQQI", "Return-of-capital income", "Taxable brokerage preferred", "Deferred taxes via ROC structure"],
        ["VYMI", "International dividends", "Taxable brokerage only", "Foreign tax credit is lost inside an IRA"],
        ["QTUM / CQTM", "Quantum computing basket", "Any", "CQTM +15.06% YTD; government encryption defense floor"],
        ["UFO / MARS", "Space sector ETF", "Any", "Owns SpaceX automatically post-inclusion"],
        ["VOO / VTI", "S&P 500 / total market", "Any", "Core anchor; Nolan's 3-move defense uses 60% here"],
    ]
    t = Table(etf_data, colWidths=[0.8 * inch, 1.35 * inch, 2.0 * inch, 2.4 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0D1B2A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F7F9FC"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    elems.append(t)
    elems.append(PageBreak())
    return elems


def section_channel_breakdowns(s):
    elems = []
    elems.append(Paragraph("4. Channel-by-Channel Breakdown", s["h1"]))
    elems.append(hr())

    # ZipTrader
    elems.append(Paragraph("ZipTrader (@ZipTrader)", s["h2"]))
    elems.append(Paragraph(
        "<b>Style:</b> Fast-paced momentum trading; small/mid-cap catalysts; sponsored segments are routine "
        "(always check the description for paid disclosures — typically $34K per slot).",
        s["body"]
    ))
    elems.append(Spacer(1, 3))
    zt_calls = [
        "INFQ: 5-catalyst playbook with $100M CHIPS Act LOI as the anchor; 30 logical qubits milestone Q4 2026",
        "BBAI: $58 bull case by 2031; Q2 earnings (~Aug 5) as 'biggest catalyst of the summer' (+15–30%)",
        "CRM (Salesforce): 'Gimme buy' after record quarter — Agentforce $1B ARR growing +265% YoY",
        "HIMS: 5 stacked catalysts; FDA peptide decision July 2026; $1.72B short interest = squeeze potential",
        "FLNC: Grid-scale battery storage; each new hyperscaler deal comparable to +20–45% move",
        "ZETA: 19 consecutive beat-and-raise; $30–$40 near-term target; first GAAP net income FY2026",
        "SpaceX ecosystem (June 17): GSAT, SATS, VSAT, ASTS as acquisition targets; RDW, FLTCF as supply chain",
        "BEAM (June 23): Base-editing biotech; 72% off ATH; first in-vivo human proof; BEAM-302 2H 2026",
    ]
    for c in zt_calls:
        elems.append(bullet(c, s["bullet"]))
    elems.append(Spacer(1, 8))

    # Felix Friends
    elems.append(Paragraph("Felix Friends (@FelixFriends)", s["h2"]))
    elems.append(Paragraph(
        "<b>Style:</b> Framework-driven investing with emphasis on timing rules ('Pattern 2 only'), "
        "position sizing (2% max on high-risk), and institutional signal reading. "
        "Winston App used for buy/stop levels. Personal positions disclosed when relevant.",
        s["body"]
    ))
    elems.append(Spacer(1, 3))
    ff_calls = [
        "NOW: 6 bipartisan politicians buying simultaneously; CEO bought $3M personal; $5B buyback; AI headwinds thesis is backwards — NOW Assist $750M and growing",
        "Nuclear power basket (NNE, OKLO, SMR, VICR, VRT): AI's real bottleneck is power; VICR and VRT most immediately actionable (profitable today, near ATHs)",
        "10-bagger framework: RGTI, QBTS, IONQ, CMPS, CMP, BBAI — all $1–10B market cap with specific 12-month catalysts",
        "TENB (Tenable): Felix personally bought at ~$23; cybersecurity budgets are non-discretionary",
        "TXG (10X Genomics): Felix's 'secret favorite'; down 85%; spatial biology + Atira platform H2 2026",
        "ADPT (Adaptive Biotechnologies): Compressed spring 10-bagger candidate; ClonoSEQ FDA-cleared MRD monopoly; profitability inflection near",
        "SpaceX IPO macro warning (June 9): $350B forced selling event; audit your 401k S&P concentration",
        "ORCL: $500B backlog; $90B revenue guided FY2026; Larry Ellison bet at its core",
    ]
    for c in ff_calls:
        elems.append(bullet(c, s["bullet"]))
    elems.append(Spacer(1, 8))

    # Wallstreet Trapper
    elems.append(Paragraph("Wallstreet Trapper (@WallstreetTrapper)", s["h2"]))
    elems.append(Paragraph(
        "<b>Style:</b> Options + buy-and-hold Freedom Index; ETF-first for new sectors; "
        "mindset/psychology content is ~50% of output. Core audience: first-generation wealth builders. "
        "Freedom Index +32% YTD (4 consecutive years of double-digit outperformance).",
        s["body"]
    ))
    elems.append(Spacer(1, 3))
    wt_calls = [
        "Memory/storage: MU, STX, WDC/SNDK are the backbone — '2–3 more years of AI memory bottleneck runway'",
        "Freedom Index holdings: Costco, EME, FIX, ITA, MU, NVDA, PWR, STX, TPL — +32% YTD",
        "Quantum: QTUM and CQTM ETFs; CQTM is the geopolitical floor (government encryption defense)",
        "Space watchlist: ASTS and RKLB as next entries; currently holds PL as space introduction",
        "GOOGL preferred over MSFT for new money — more AI upside; MSFT: hold, don't abandon",
        "SpaceX: consistent bearish view on IPO valuation (~100x revenue); use UFO/NASA/MARS ETFs instead",
        "GS: Banks turning + SpaceX IPO underwriting catalyst; 'if you can't afford GS, get Morgan Stanley'",
        "AI supercycle: 10-year macro thesis; $6T sitting on sidelines; institutions buy every dip at key levels",
    ]
    for c in wt_calls:
        elems.append(bullet(c, s["bullet"]))
    elems.append(Spacer(1, 8))

    # Nolan Gouveia
    elems.append(Paragraph("Nolan Gouveia (@NolanGouveia)", s["h2"]))
    elems.append(Paragraph(
        "<b>Style:</b> Passive income optimization; retirement-focused; ETF placement strategy; "
        "no individual stock picks. Two videos in the covered period — both highly actionable for "
        "dividend investors.",
        s["body"]
    ))
    elems.append(Spacer(1, 3))
    ng_calls = [
        "Financial repression is active: -2.4% real yield on savings; the quiet tax eroding purchasing power",
        "Three-move defense: 60% SCHD/VYM/VOO, 25% TIPS ladder, 15% HYSA — projects +$44K vs savings on $100K over 10 years",
        "5 Laws of ETF Placement: SCHD anywhere; JEPI/JEPQ in tax-advantaged only; SPYI/QQQI in taxable; VYMI in taxable for foreign tax credit; bonds in tax-advantaged",
        "SCHD stats: 11.6% 5-year dividend CAGR; 3.3% current yield; 5-year total return ~9.2%",
        "JEPI/JEPQ in a taxable brokerage is the '$7,000 JEPI Tax Trap' — most commonly made placement mistake",
    ]
    for c in ng_calls:
        elems.append(bullet(c, s["bullet"]))
    elems.append(PageBreak())
    return elems


def section_catalyst_calendar(s):
    elems = []
    elems.append(Paragraph("5. Watchlist & Catalyst Calendar", s["h1"]))
    elems.append(hr())
    elems.append(Paragraph(
        "Key dates and events to monitor based on the covered period. "
        "All dates approximate unless noted.",
        s["body"]
    ))
    elems.append(Spacer(1, 6))

    cal_data = [
        ["Date", "Ticker", "Event", "Potential Move"],
        ["Jul 6–9, 2026", "BEAM", "BEAM-304 PKU trial — wildcard data readout", "+5 to +15%"],
        ["July 2026", "HIMS", "FDA peptide decision", "Material; binary"],
        ["Jul–Sep 2026", "INFQ", "CHIPS Act LOI → Final deal conversion", "+25 to +50%"],
        ["Late June 2026", "ZENA*", "Russell 3000 index inclusion (paid sponsor — disregard)", "N/A"],
        ["~Aug 5, 2026", "BBAI", "Q2 earnings (ZipTrader: 'biggest catalyst of the summer')", "+15 to +30%"],
        ["Aug 13, 2026", "INFQ", "Q2 earnings vs. $40M guide", "+15 to +25%"],
        ["Q3 2026", "INFQ", "Next NVDA logical qubit demo", "+15 to +35%"],
        ["2H 2026", "BEAM", "BEAM-302 AATD in-vivo data readout (key catalyst)", "±20 to +35%"],
        ["2H 2026", "RGTI", "Lyra chip + $100M CHIPS Act deal; NVDA integration", "+30 to +60%"],
        ["Q4 2026", "INFQ", "30 logical qubits milestone; Quantum Spectrum first customer", "+20 to +60%"],
        ["Nov 12, 2026", "INFQ", "Q3 earnings", "+15 to +25%"],
        ["Year-end 2026", "BEAM", "Sickle cell (RISTO-CEL) BLA filing", "+8 to +20%"],
        ["Dec 8, 2026", "SpaceX", "180-day lockup expires — major insider selling event", "SpaceX −; ecosystem +"],
        ["2026 Q4", "TXG", "Atira platform launch + Bioptimus AI partnership", "Re-rating potential"],
        ["Jun 12, 2027", "SpaceX", "Elon's personal mega-block of shares unlocks", "SpaceX risk event"],
    ]
    t = Table(cal_data, colWidths=[1.15 * inch, 0.85 * inch, 3.3 * inch, 1.25 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0D1B2A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F7F9FC"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    elems.append(t)
    elems.append(Spacer(1, 6))
    elems.append(Paragraph(
        "* ZENA is a paid sponsored segment ($34K) — not an independent catalyst.",
        ParagraphStyle("footnote", parent=s["caption"], alignment=TA_LEFT,
                       textColor=colors.HexColor("#999999"))
    ))
    elems.append(Spacer(1, 16))

    elems.append(Paragraph("Stocks to Watch — Condensed Watchlist", s["h2"]))
    watch_data = [
        ["Ticker", "Current Angle", "Source"],
        ["MU", "AI memory bottleneck; options + buy-hold", "W.Trapper"],
        ["BEAM", "Biotech compounder 72% off ATH; in-vivo first human proof", "ZipTrader"],
        ["GSAT", "SpaceX acquisition candidate #1; spectrum play", "ZipTrader"],
        ["NOW", "Politicians + CEO buying; AI platform thesis; $5B buyback", "Felix, ZipTrader"],
        ["HIMS", "FDA July catalyst; short squeeze setup; 57% off highs", "ZipTrader"],
        ["RGTI", "Quantum: CHIPS LOI + Lyra chip + NVDA integration", "Felix, ZipTrader"],
        ["INFQ", "Quantum pure-play; $40M 2026 guide; 30 qubits Q4 2026", "ZipTrader"],
        ["FLNC", "AI power infrastructure; $5.6B backlog; next deal = 20-45%", "ZipTrader"],
        ["ZETA", "19 qtrs beat-and-raise; first GAAP profit 2026; $30-40 target", "ZipTrader"],
        ["VRT", "Data center cooling + power; profitable; near ATH", "Felix"],
        ["ASTS", "SpaceX direct-to-phone competitor; W.Trapper 'coming soon'", "ZipTrader, W.Trapper"],
        ["ADPT", "Blood cancer MRD monopoly; profitability inflection near; 87% off ATH", "Felix"],
        ["SCHD", "Core dividend ETF; 11.6% div CAGR; place anywhere", "Nolan"],
    ]
    t = Table(watch_data, colWidths=[0.85 * inch, 4.4 * inch, 1.3 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A3A5C")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F0F5FB"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elems.append(t)
    elems.append(Spacer(1, 20))

    elems.append(hr("#CCCCCC", 0.5))
    elems.append(Spacer(1, 6))
    elems.append(Paragraph(
        "DISCLAIMER: This document is a summary of publicly available YouTube content created for "
        "informational and educational purposes only. It does not constitute financial advice, investment "
        "recommendations, or an offer to buy or sell any security. Sponsored segments within the covered "
        "videos are noted and should not be treated as independent research. Past performance of any "
        "mentioned security does not guarantee future results. All investment decisions should be made "
        "after conducting your own due diligence and consulting a qualified financial professional.",
        s["disclaimer"]
    ))
    return elems


# ── Build ─────────────────────────────────────────────────────────────────────

def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT,
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title="Stock YouTubers Channel Brief — June 2026",
        author="build-wiki auto-compiler",
    )

    s = build_styles()
    story = []
    story += cover_page(s)
    story += toc_page(s)
    story += section_executive_summary(s)
    story += section_macro(s)
    story += section_stock_ideas(s)
    story += section_channel_breakdowns(s)
    story += section_catalyst_calendar(s)

    doc.build(story)
    print(f"PDF written to: {OUTPUT}")


if __name__ == "__main__":
    build_pdf()
