from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
from app.database import get_db
from app.models.contract import Contract
from app.models.negotiation import NegotiationSession

router = APIRouter(prefix="/contract", tags=["contract"])


@router.get("/{session_id}/pdf")
def get_contract_pdf(session_id: str, db: Session = Depends(get_db)):
    contract = db.query(Contract).filter(Contract.session_id == session_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    if not contract.pdf_file_path or not os.path.exists(contract.pdf_file_path):
        raise HTTPException(status_code=404, detail="PDF file not found")

    return FileResponse(
        path=contract.pdf_file_path,
        filename=f"contract_{session_id}.pdf",
        media_type="application/pdf"
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
