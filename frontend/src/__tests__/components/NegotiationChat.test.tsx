import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { NegotiationChat } from '@/components/NegotiationChat';
import { ProposalAction } from '@/types/proposal';

describe('NegotiationChat', () => {
  it('shows empty state when no bids', () => {
    render(<NegotiationChat bids={[]} />);
    expect(screen.getByText(/no bids yet/i)).toBeInTheDocument();
  });

  it('renders bid bubbles', () => {
    const bids = [
      {
        price: 45000,
        delivery_days: 30,
        sla_percent: 3.5,
        action: ProposalAction.OFFER,
        justification: 'Opening bid',
        round_number: 1,
        agent_type: 'BUYER' as const,
      },
    ];
    render(<NegotiationChat bids={bids} />);
    expect(screen.getByText('BUYER')).toBeInTheDocument();
    expect(screen.getByText('$45,000')).toBeInTheDocument();
  });
});
