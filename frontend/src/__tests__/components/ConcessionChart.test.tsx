import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ConcessionChart } from '@/components/ConcessionChart';
import { ProposalAction } from '@/types/proposal';

describe('ConcessionChart', () => {
  it('shows empty state when no bids', () => {
    render(<ConcessionChart bids={[]} />);
    expect(screen.getByText(/waiting for negotiation/i)).toBeInTheDocument();
  });

  it('renders chart when bids exist', () => {
    const bids = [
      { price: 45000, delivery_days: 30, sla_percent: 3.5, action: ProposalAction.OFFER, justification: '', round_number: 1, agent_type: 'BUYER' as const },
      { price: 47000, delivery_days: 35, sla_percent: 3.0, action: ProposalAction.OFFER, justification: '', round_number: 1, agent_type: 'VENDOR' as const },
    ];
    render(<ConcessionChart bids={bids} />);
    expect(screen.getByText('Concession Curves')).toBeInTheDocument();
  });
});
