import json
import re
import httpx

from app.agents.base import BaseAgent
from app.agents.buyer import BuyerAgent
from app.agents.vendor import VendorAgent
from app.schemas.proposal import ProposalBid, NegotiationState, ProposalAction
from app.schemas.policy import BuyerPolicyEnvelope, VendorPolicyEnvelope
from app.config import settings


# ── Low-level HTTP bridge (synchronous) ───────────────────────────────────────

def call_studio_agent(agent_id: str, session_id: str, message: str) -> str:
    """
    POST to the official Lyzr Agent Studio REST API.

    Endpoint : https://agent-prod.studio.lyzr.ai/v3/agent/{agent_id}/chat
    Auth     : x-api-key header (NOT a Bearer token)
    Payload  : {user_id, agent_id, session_id, message}
    Returns  : raw response text from the Studio agent
    """
    url = f"{settings.LYZR_API_URL.rstrip('/')}/v3/inference/chat/"
    headers = {
        "x-api-key": settings.LYZR_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "user_id": f"negotiation-{session_id}",
        "agent_id": agent_id,
        "session_id": session_id,
        "message": message,
    }
    with httpx.Client(timeout=30) as client:
        response = client.post(url, json=payload, headers=headers)
        response.raise_for_status()
    return response.json().get("response", "")


def parse_bid_from_response(
    text: str,
    round_number: int,
    agent_type: str,
) -> ProposalBid:
    """
    Extract the first JSON object from the Studio agent's response.
    The LLM may wrap JSON in prose — the regex handles that gracefully.
    """
    match = re.search(r"\{[^{}]+\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in agent response: {text!r}")
    data = json.loads(match.group())
    return ProposalBid(
        price=float(data.get("price", 0)),
        delivery_days=int(data.get("delivery_days", 0)),
        sla_percent=float(data.get("sla_percent", data.get("sla_penalty_percent", 0))),
        action=ProposalAction(data.get("action", "OFFER")),
        justification=data.get("justification", data.get("justification_text", "")),
        round_number=round_number,
        agent_type=agent_type,
    )


# ── Agent adapter (implements BaseAgent interface) ────────────────────────────

_CIRCUIT_BREAKER_TRIPPED = False

class LyzrAgentAdapter(BaseAgent):
    """
    Wraps the Lyzr Agent Studio REST API behind the same BaseAgent interface
    as BuyerAgent / VendorAgent.

    Architecture:
        Lyzr Agent Studio  →  call_studio_agent()  →  parse_bid_from_response()
        → Safe AI Arbiter (validate_with_retry)  →  SQLAlchemy

    Falls back to the deterministic agent on any network or parse failure so a
    bad API response never crashes a live demo.
    """

    def __init__(
        self,
        agent_type: str,
        agent_id: str,
        fallback_agent: BaseAgent,
    ):
        super().__init__(agent_type)
        self.agent_id = agent_id
        self._fallback = fallback_agent

    def generate_offer(self, state: NegotiationState) -> ProposalBid:
        """
        1. Call the Lyzr Agent API (The Bridge)
        2. Parse into Pydantic schema (Python Models)
        3. Return bid — Arbiter validation happens in the orchestrator
        Falls back to deterministic agent on any failure.
        """
        global _CIRCUIT_BREAKER_TRIPPED

        if not settings.LYZR_API_KEY or not self.agent_id:
            return self._fallback.generate_offer(state)
        
        if _CIRCUIT_BREAKER_TRIPPED:
            return self._fallback.generate_offer(state)
        
        try:
            message = self._build_message(state)
            raw = call_studio_agent(self.agent_id, state.session_id, message)
            return parse_bid_from_response(raw, state.current_round, self.agent_type)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 402:
                print(f"Lyzr Agent Error ({self.agent_type}): 402 Payment Required. Tripping circuit breaker globally.")
                _CIRCUIT_BREAKER_TRIPPED = True
            else:
                print(f"Lyzr Agent HTTP Error ({self.agent_type}): {e}.")
            return self._fallback.generate_offer(state)
        except Exception as e:
            # Fallback to deterministic agent if Lyzr API is out of credits (402), down, or hallucinates
            print(f"Lyzr Agent Error ({self.agent_type}): {e}. Falling back to deterministic agent.")
            return self._fallback.generate_offer(state)

    def _build_message(self, state: NegotiationState) -> str:
        """Build the negotiation context message sent to the Studio agent."""
        history_str = "\n".join([
            f"Round {h.round_number}: {h.agent_type} offered "
            f"${h.price:,.0f}, {h.delivery_days} days, {h.sla_percent}% SLA"
            for h in state.history[-6:]   # last 6 bids for context window efficiency
        ]) or "No history yet — make your opening offer."

        return (
            f"Negotiation round {state.current_round} of {state.max_rounds}.\n"
            f"Recent history:\n{history_str}\n\n"
            "Generate your next offer. Respond ONLY with a JSON object:\n"
            '{"price": <float>, "delivery_days": <int>, "sla_percent": <float>, '
            '"action": "OFFER"|"ACCEPT"|"END_NEGOTIATION", "justification": "<one sentence>"}'
        )


# ── Factory functions (called by orchestrator) ────────────────────────────────

def make_lyzr_buyer(policy: BuyerPolicyEnvelope) -> LyzrAgentAdapter:
    """Create a Lyzr-powered Buyer agent with deterministic BuyerAgent as fallback."""
    return LyzrAgentAdapter(
        agent_type="BUYER",
        agent_id=settings.LYZR_BUYER_AGENT_ID,
        fallback_agent=BuyerAgent(policy),
    )


def make_lyzr_vendor(policy: VendorPolicyEnvelope) -> LyzrAgentAdapter:
    """Create a Lyzr-powered Vendor agent with deterministic VendorAgent as fallback."""
    return LyzrAgentAdapter(
        agent_type="VENDOR",
        agent_id=settings.LYZR_VENDOR_AGENT_ID,
        fallback_agent=VendorAgent(policy),
    )
