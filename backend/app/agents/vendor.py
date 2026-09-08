from app.agents.base import BaseAgent
from app.schemas.proposal import ProposalBid, ProposalAction, NegotiationState
from app.schemas.policy import VendorPolicyEnvelope
from app.engine.concession import calculate_concession


class VendorAgent(BaseAgent):
    def __init__(self, policy: VendorPolicyEnvelope):
        super().__init__("VENDOR")
        self.policy = policy
        self._initial_price = 49000
        self._initial_delivery = 40
        self._initial_sla = 2.0

    def generate_offer(self, state: NegotiationState) -> ProposalBid:
        if state.history:
            last_offer = state.history[-1]
            if last_offer.agent_type == "BUYER" and last_offer.action == ProposalAction.OFFER:
                return self._evaluate_buyer_offer(last_offer, state)
            if last_offer.agent_type == "VENDOR" and last_offer.action == ProposalAction.ACCEPT:
                return ProposalBid(
                    price=last_offer.price,
                    delivery_days=last_offer.delivery_days,
                    sla_percent=last_offer.sla_percent,
                    action=ProposalAction.ACCEPT,
                    justification="Accepting buyer's final terms",
                    round_number=state.current_round,
                    agent_type="VENDOR"
                )

        gap_price = self._initial_price - self.policy.min_price
        gap_delivery = self.policy.min_delivery_days - self._initial_delivery
        gap_sla = self._initial_sla - self.policy.max_sla_percent

        concession = calculate_concession(
            base_gap_price=gap_price,
            base_gap_delivery=gap_delivery,
            base_gap_sla=gap_sla,
            round_number=state.current_round,
            discount_factor=0.85
        )

        price = self._initial_price - concession["price"]
        delivery = int(self._initial_delivery - concession["delivery"])
        sla = self._initial_sla + concession["sla"]

        return ProposalBid(
            price=max(price, self.policy.min_price),
            delivery_days=max(delivery, self.policy.min_delivery_days),
            sla_percent=min(sla, self.policy.max_sla_percent),
            action=ProposalAction.OFFER,
            justification=f"Opening counter-bid round {state.current_round}",
            round_number=state.current_round,
            agent_type="VENDOR"
        )

    def _evaluate_buyer_offer(self, buyer_bid: ProposalBid, state: NegotiationState) -> ProposalBid:
        if (buyer_bid.price >= self.policy.min_price and
            buyer_bid.delivery_days >= self.policy.min_delivery_days and
            buyer_bid.sla_percent <= self.policy.max_sla_percent):
            return ProposalBid(
                price=buyer_bid.price,
                delivery_days=buyer_bid.delivery_days,
                sla_percent=buyer_bid.sla_percent,
                action=ProposalAction.ACCEPT,
                justification="Accepting buyer terms within policy",
                round_number=state.current_round,
                agent_type="VENDOR"
            )

        concession = calculate_concession(
            base_gap_price=buyer_bid.price - self.policy.min_price,
            base_gap_delivery=self.policy.min_delivery_days - buyer_bid.delivery_days,
            base_gap_sla=buyer_bid.sla_percent - self.policy.max_sla_percent,
            round_number=state.current_round,
            discount_factor=0.85
        )

        new_price = max(buyer_bid.price - concession["price"] * 0.5, self.policy.min_price)
        new_delivery = max(buyer_bid.delivery_days, self.policy.min_delivery_days)
        new_sla = min(buyer_bid.sla_percent + concession["sla"] * 0.3, self.policy.max_sla_percent)

        return ProposalBid(
            price=new_price,
            delivery_days=new_delivery,
            sla_percent=new_sla,
            action=ProposalAction.OFFER,
            justification=f"Counter-offer round {state.current_round}",
            round_number=state.current_round,
            agent_type="VENDOR"
        )
