import json
from datetime import datetime, timezone
from pathlib import Path
import httpx
from app.config import settings
from app.schemas.proposal import ProposalBid


class LyzrAIMSLogger:
    def __init__(self):
        self._enabled = bool(settings.LYZR_API_KEY)
        self.log_path = Path(__file__).resolve().parents[2] / "aims_audit_trail.jsonl"

    def log_proposal(self, session_id: str, bid: ProposalBid, validated: bool):
        payload = {
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent_type": bid.agent_type,
            "round_number": bid.round_number,
            "price": bid.price,
            "delivery_days": bid.delivery_days,
            "sla_percent": bid.sla_percent,
            "action": getattr(bid.action, "value", str(bid.action)),
            "justification": bid.justification,
            "validated": validated
        }

        # 1. Always record the local audit trail
        self._log_locally(payload)

        # 2. Sync to cloud governance if API key is active
        if self._enabled:
            self._push_to_aims(payload)

    def _push_to_aims(self, payload: dict):
        try:
            response = httpx.post(
                f"{settings.LYZR_API_URL}/aims/log",
                headers={
                    "x-api-key": settings.LYZR_API_KEY,
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=5.0
            )
            response.raise_for_status()
        except Exception:
            # Cloud delivery failure won't interrupt negotiation or local trail
            pass

    def _log_locally(self, payload: dict):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "AIMS_AUDIT_LOG",
            "payload": payload,
        }
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")


aims_logger = LyzrAIMSLogger()
