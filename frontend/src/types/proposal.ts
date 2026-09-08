export enum ProposalAction {
  OFFER = 'OFFER',
  ACCEPT = 'ACCEPT',
  END_NEGOTIATION = 'END_NEGOTIATION',
}

export interface ProposalBid {
  price: number;
  delivery_days: number;
  sla_percent: number;
  action: ProposalAction;
  justification: string;
  round_number: number;
  agent_type: 'BUYER' | 'VENDOR';
}

export interface NegotiationState {
  session_id: string;
  current_round: number;
  max_rounds: number;
  history: ProposalBid[];
  is_complete: boolean;
  consensus: ProposalBid | null;
}

export interface RoundResponse {
  round_number: number;
  agent_type: string;
  price: number;
  delivery_days: number;
  sla_percent: number;
  action: string;
  justification: string;
}
