"""Safe AI Arbiter — deterministic policy enforcement layer.

The Arbiter is a mathematical firewall that sits between the AI agents
and the negotiation state machine.  Before any bid is recorded, it
validates the proposal against the user's hard policy limits (e.g.,
max budget, min SLA).  If an agent hallucinates or produces an
out-of-bounds offer, the Arbiter rejects it and forces a retry.
"""

from app.schemas.proposal import ProposalBid, ProposalAction, NegotiationState
from app.schemas.policy import BuyerPolicyEnvelope, VendorPolicyEnvelope
from typing import Union


def validate_proposal(
    proposal: ProposalBid,
    policy: Union[BuyerPolicyEnvelope, VendorPolicyEnvelope],
    agent_type: str
) -> bool:
    """Check whether a single proposal respects the agent's policy envelope.

    Accepts and end-negotiation actions are always considered valid.
    For offers, the proposal's price, delivery days, and SLA percentage
    are checked against the hard limits defined in the policy.

    Args:
        proposal: The bid to validate.
        policy: The agent's policy envelope containing hard limits.
        agent_type: ``"BUYER"`` or ``"VENDOR"``.

    Returns:
        ``True`` if the proposal is within bounds, ``False`` otherwise.
    """
    if proposal.action == ProposalAction.ACCEPT:
        return True
    if proposal.action == ProposalAction.END_NEGOTIATION:
        return True

    if agent_type == "BUYER":
        return _validate_buyer(proposal, policy)
    else:
        return _validate_vendor(proposal, policy)


def _validate_buyer(proposal: ProposalBid, policy: BuyerPolicyEnvelope) -> bool:
    if proposal.price > policy.max_budget:
        return False
    if proposal.delivery_days > policy.max_delivery_days:
        return False
    if proposal.sla_percent < policy.min_sla_percent:
        return False
    return True


def _validate_vendor(proposal: ProposalBid, policy: VendorPolicyEnvelope) -> bool:
    if proposal.price < policy.min_price:
        return False
    if proposal.delivery_days < policy.min_delivery_days:
        return False
    if proposal.sla_percent > policy.max_sla_percent:
        return False
    return True


def validate_with_retry(
    agent,
    state: NegotiationState,
    policy: Union[BuyerPolicyEnvelope, VendorPolicyEnvelope],
    max_retries: int = 3
) -> ProposalBid:
    """Request a proposal from *agent* and validate it, retrying on failure.

    If the agent produces an out-of-bounds proposal, it is silently
    discarded and the agent is asked again.  This is critical when
    using LLM-backed agents (Lyzr) whose outputs may occasionally
    hallucinate values outside the policy envelope.

    Args:
        agent: Any object implementing ``generate_offer(state)``.
        state: The current negotiation state.
        policy: Hard limits to validate against.
        max_retries: Maximum number of attempts before raising.

    Returns:
        The first valid :class:`ProposalBid`.

    Raises:
        ValueError: If no valid proposal is produced within *max_retries*.
    """
    from app.schemas.proposal import NegotiationState as NS

    for attempt in range(max_retries):
        proposal = agent.generate_offer(state)
        if validate_proposal(proposal, policy, agent.agent_type):
            return proposal
    raise ValueError(f"Agent failed to produce valid proposal after {max_retries} attempts")
