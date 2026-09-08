from app.schemas.proposal import ProposalBid, ProposalAction, NegotiationState
from app.schemas.policy import BuyerPolicyEnvelope, VendorPolicyEnvelope
from typing import Union


def validate_proposal(
    proposal: ProposalBid,
    policy: Union[BuyerPolicyEnvelope, VendorPolicyEnvelope],
    agent_type: str
) -> bool:
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
    from app.schemas.proposal import NegotiationState as NS

    for attempt in range(max_retries):
        proposal = agent.generate_offer(state)
        if validate_proposal(proposal, policy, agent.agent_type):
            return proposal
    raise ValueError(f"Agent failed to produce valid proposal after {max_retries} attempts")
