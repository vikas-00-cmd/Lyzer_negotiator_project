from app.agents.base import BaseAgent
from app.schemas.proposal import ProposalBid, ProposalAction, NegotiationState
from app.schemas.policy import BuyerPolicyEnvelope
from app.engine.concession import calculate_concession


class BuyerAgent(BaseAgent):
    def __init__(self, policy: BuyerPolicyEnvelope):
        super().__init__("BUYER")
        self.policy = policy
        self._initial_price = 40000
        self._initial_delivery = 20
        self._initial_sla = 5.0

    def generate_offer(self, state: NegotiationState) -> ProposalBid:
        if state.history:
            last_offer = state.history[-1]
            if last_offer.agent_type == "VENDOR" and last_offer.action == ProposalAction.OFFER:
                return self._evaluate_vendor_offer(last_offer, state)
            if last_offer.agent_type == "BUYER" and last_offer.action == ProposalAction.ACCEPT:
                return ProposalBid(
                    price=last_offer.price,
                    delivery_days=last_offer.delivery_days,
                    sla_percent=last_offer.sla_percent,
                    action=ProposalAction.ACCEPT,
                    justification="Accepting vendor's final terms",
                    round_number=state.current_round,
                    agent_type="BUYER"
                )

        gap_price = self.policy.max_budget - self._initial_price
        gap_delivery = self._initial_delivery - 0
        gap_sla = self._initial_sla - self.policy.min_sla_percent

        concession = calculate_concession(
            base_gap_price=gap_price,
            base_gap_delivery=gap_delivery,
            base_gap_sla=gap_sla,
            round_number=state.current_round,
            discount_factor=0.85
        )

        price = self._initial_price + concession["price"]
        delivery = int(self._initial_delivery + concession["delivery"])
        sla = self._initial_sla - concession["sla"]

        return ProposalBid(
            price=min(price, self.policy.max_budget),
            delivery_days=min(delivery, self.policy.max_delivery_days),
            sla_percent=max(sla, self.policy.min_sla_percent),
            action=ProposalAction.OFFER,
            justification=f"Opening bid round {state.current_round}",
            round_number=state.current_round,
            agent_type="BUYER"
        )

    def _evaluate_vendor_offer(self, vendor_bid: ProposalBid, state: NegotiationState) -> ProposalBid:
        if (vendor_bid.price <= self.policy.max_budget and
            vendor_bid.delivery_days <= self.policy.max_delivery_days and
            vendor_bid.sla_percent >= self.policy.min_sla_percent):
            return ProposalBid(
                price=vendor_bid.price,
                delivery_days=vendor_bid.delivery_days,
                sla_percent=vendor_bid.sla_percent,
                action=ProposalAction.ACCEPT,
                justification="Accepting vendor terms within policy",
                round_number=state.current_round,
                agent_type="BUYER"
            )

        concession = calculate_concession(
            base_gap_price=self.policy.max_budget - vendor_bid.price,
            base_gap_delivery=vendor_bid.delivery_days - 0,
            base_gap_sla=vendor_bid.sla_percent - self.policy.min_sla_percent,
            round_number=state.current_round,
            discount_factor=0.85
        )

        new_price = min(vendor_bid.price + concession["price"] * 0.5, self.policy.max_budget)
        new_delivery = min(vendor_bid.delivery_days, self.policy.max_delivery_days)
        new_sla = max(vendor_bid.sla_percent - concession["sla"] * 0.3, self.policy.min_sla_percent)

        return ProposalBid(
            price=new_price,
            delivery_days=new_delivery,
            sla_percent=new_sla,
            action=ProposalAction.OFFER,
            justification=f"Counter-offer round {state.current_round}",
            round_number=state.current_round,
            agent_type="BUYER"
        )
