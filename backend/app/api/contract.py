from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.contract import Contract
from app.models.negotiation import NegotiationSession
from app.schemas.contract import ContractPayload
from app.engine.consensus import generate_pdf_bytes

router = APIRouter(prefix="/contract", tags=["contract"])


@router.get("/{session_id}/pdf")
def get_contract_pdf(session_id: str, db: Session = Depends(get_db)):
    session_data = db.query(NegotiationSession).filter(NegotiationSession.id == session_id).first()
    if not session_data or not session_data.contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    # Extract justifications from the last rounds
    last_buyer_bid = next((r for r in reversed(session_data.rounds) if r.agent_type == "BUYER"), None)
    last_vendor_bid = next((r for r in reversed(session_data.rounds) if r.agent_type == "VENDOR"), None)

    # Reconstruct the payload for PDF generation
    payload = ContractPayload(
        session_id=session_id,
        final_price=session_data.contract.final_price,
        final_delivery_days=session_data.contract.final_delivery_days,
        final_sla_percent=session_data.contract.final_sla_percent,
        buyer_justification=last_buyer_bid.justification if last_buyer_bid else "",
        vendor_justification=last_vendor_bid.justification if last_vendor_bid else "",
        total_rounds=session_data.current_round
    )

    pdf_buffer = generate_pdf_bytes(payload)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=contract_{session_id}.pdf"}
    )


@router.get("/{session_id}/details")
def get_contract_details(session_id: str, db: Session = Depends(get_db)):
    contract = db.query(Contract).filter(Contract.session_id == session_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    return {
        "id": contract.id,
        "session_id": contract.session_id,
        "final_price": contract.final_price,
        "final_delivery_days": contract.final_delivery_days,
        "final_sla_percent": contract.final_sla_percent,
        "pdf_file_path": contract.pdf_file_path,
        "created_at": contract.created_at.isoformat()
    }
