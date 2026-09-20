"""Contract generation and in-memory PDF rendering.

When the negotiation reaches consensus (ACCEPTED status), this module
extracts the agreed terms, persists a :class:`Contract` record, and
provides an on-the-fly PDF generator that streams directly to the
browser via ``io.BytesIO`` — completely bypassing ephemeral disk storage.
"""

import io
from sqlalchemy.orm import Session
from app.models.negotiation import NegotiationSession
from app.models.contract import Contract
from app.schemas.proposal import NegotiationState, ProposalBid
from app.schemas.contract import ContractPayload
from app.config import settings


def generate_contract(db: Session, session: NegotiationSession, state: NegotiationState):
    """Extract consensus terms from the negotiation and persist a contract record.

    Locates the final accepted bid from the negotiation history,
    constructs a :class:`ContractPayload`, and saves a :class:`Contract`
    row to the database.  The PDF is *not* generated here — it is
    rendered on-demand by :func:`generate_pdf_bytes` when the user
    requests a download.

    Args:
        db: Active SQLAlchemy database session.
        session: The negotiation session that reached consensus.
        state: The full negotiation state including bid history.

    Returns:
        The newly created :class:`Contract` record.

    Raises:
        ValueError: If no consensus bid can be found in the history.
    """
    consensus = state.consensus
    if not consensus:
        for bid in reversed(state.history):
            if bid.agent_type == "VENDOR":
                consensus = bid
                break

    if not consensus:
        raise ValueError("No consensus found")

    last_buyer_bid = None
    last_vendor_bid = None
    for bid in reversed(state.history):
        if bid.agent_type == "BUYER" and not last_buyer_bid:
            last_buyer_bid = bid
        if bid.agent_type == "VENDOR" and not last_vendor_bid:
            last_vendor_bid = bid
        if last_buyer_bid and last_vendor_bid:
            break

    payload = ContractPayload(
        session_id=session.id,
        final_price=consensus.price,
        final_delivery_days=consensus.delivery_days,
        final_sla_percent=consensus.sla_percent,
        buyer_justification=last_buyer_bid.justification if last_buyer_bid else "",
        vendor_justification=last_vendor_bid.justification if last_vendor_bid else "",
        total_rounds=state.current_round
    )

    contract = Contract(
        session_id=session.id,
        final_price=payload.final_price,
        final_delivery_days=payload.final_delivery_days,
        final_sla_percent=payload.final_sla_percent
    )
    db.add(contract)
    db.commit()
    db.refresh(contract)

    return contract


def generate_pdf_bytes(payload: ContractPayload) -> io.BytesIO:
    """Render a legally formatted PDF contract entirely in memory.

    Uses ReportLab to build a professional contract document containing
    the agreed commercial terms, negotiation justifications, and
    signature blocks.  The PDF is written to an ``io.BytesIO`` buffer
    (never to disk), making it immune to ephemeral filesystem wipes
    on cloud platforms like Render.

    Args:
        payload: The contract data including final price, delivery,
            SLA, justifications, and session metadata.

    Returns:
        A seeked-to-zero ``io.BytesIO`` buffer containing the PDF bytes,
        ready to be streamed via FastAPI's ``StreamingResponse``.
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    )

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=inch,
        rightMargin=inch,
        topMargin=inch,
        bottomMargin=inch,
    )
    styles = getSampleStyleSheet()
    elements = []

    # ── Header ────────────────────────────────────────────────────────────────
    title_style = ParagraphStyle(
        "ContractTitle",
        parent=styles["Title"],
        fontSize=20,
        leading=26,
        textColor=colors.HexColor("#1a2e5a"),
    )
    elements.append(Paragraph("B2B Supply Chain &amp; SLA Agreement", title_style))
    elements.append(Spacer(1, 6))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a2e5a")))
    elements.append(Spacer(1, 10))

    meta_style = ParagraphStyle(
        "Meta",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.grey,
    )
    elements.append(Paragraph(f"Session ID: {payload.session_id}", meta_style))
    elements.append(Paragraph(
        f"Executed: {payload.created_at.strftime('%B %d, %Y at %H:%M UTC')}",
        meta_style,
    ))
    elements.append(Spacer(1, 20))

    # ── Agreed Terms Table ─────────────────────────────────────────────────────
    elements.append(Paragraph("Agreed Commercial Terms", styles["Heading2"]))
    elements.append(Spacer(1, 8))

    terms_data = [
        ["Term", "Agreed Value"],
        ["Final Contract Price", f"${payload.final_price:,.2f}"],
        ["Delivery Window", f"{payload.final_delivery_days} Days"],
        ["SLA Penalty Rate", f"{payload.final_sla_percent:.1f}%"],
        ["Total Negotiation Rounds", str(payload.total_rounds)],
    ]

    col_widths = [3 * inch, 3 * inch]
    table = Table(terms_data, colWidths=col_widths)
    table.setStyle(TableStyle([
        # Header row
        ("BACKGROUND",    (0, 0), (-1, 0), colors.HexColor("#1a2e5a")),
        ("TEXTCOLOR",     (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 11),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("TOPPADDING",    (0, 0), (-1, 0), 10),
        # Data rows alternating
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4ff")]),
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -1), 10),
        ("ALIGN",         (1, 0), (1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 1), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
        # Grid
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#b0bcd4")),
        ("BOX",           (0, 0), (-1, -1), 1.5, colors.HexColor("#1a2e5a")),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))

    # ── Justifications ─────────────────────────────────────────────────────────
    elements.append(Paragraph("Negotiation Justifications", styles["Heading2"]))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(
        f"<b>Buyer:</b> {payload.buyer_justification or 'Terms accepted.'}",
        styles["Normal"],
    ))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(
        f"<b>Vendor:</b> {payload.vendor_justification or 'Terms accepted.'}",
        styles["Normal"],
    ))
    elements.append(Spacer(1, 30))

    # ── Signature Block ────────────────────────────────────────────────────────
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    elements.append(Spacer(1, 14))
    elements.append(Paragraph("Execution &amp; Signatures", styles["Heading2"]))
    elements.append(Spacer(1, 8))

    sig_data = [
        ["Buyer Authorized Signature", "Vendor Authorized Signature"],
        ["\n\n________________________", "\n\n________________________"],
        ["Name: ___________________", "Name: ___________________"],
        ["Title: __________________", "Title: __________________"],
        ["Date:  ___________________", "Date:  ___________________"],
    ]
    sig_table = Table(sig_data, colWidths=[3 * inch, 3 * inch])
    sig_table.setStyle(TableStyle([
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("ALIGN",         (0, 0), (-1, -1), "LEFT"),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(sig_table)

    # ── Footer note ────────────────────────────────────────────────────────────
    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    elements.append(Spacer(1, 6))
    footer_style = ParagraphStyle(
        "Footer", parent=styles["Normal"], fontSize=8, textColor=colors.grey
    )
    elements.append(Paragraph(
        "This agreement was autonomously negotiated and validated by the Lyzr B2B "
        "Negotiation Platform. All bids were verified by the Safe AI Arbiter and "
        "logged to the AIMS governance audit trail.",
        footer_style,
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer
