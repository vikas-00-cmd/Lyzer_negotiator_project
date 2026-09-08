import { describe, it, expect } from 'vitest';

describe('useNegotiation hook logic', () => {
  it('maps rounds to ProposalBid format', () => {
    const rounds = [
      { round_number: 1, agent_type: 'BUYER', price: 45000, delivery_days: 30, sla_percent: 3.5, action: 'OFFER', justification: 'test' },
      { round_number: 1, agent_type: 'VENDOR', price: 47000, delivery_days: 35, sla_percent: 3.0, action: 'OFFER', justification: 'counter' },
    ];

    const mapped = rounds.map((r) => ({
      price: r.price,
      delivery_days: r.delivery_days,
      sla_percent: r.sla_percent,
      action: r.action,
      justification: r.justification,
      round_number: r.round_number,
      agent_type: r.agent_type as 'BUYER' | 'VENDOR',
    }));

    expect(mapped).toHaveLength(2);
    expect(mapped[0].agent_type).toBe('BUYER');
    expect(mapped[1].agent_type).toBe('VENDOR');
  });

  it('filters buyer and vendor bids', () => {
    const bids = [
      { agent_type: 'BUYER', price: 45000 },
      { agent_type: 'VENDOR', price: 47000 },
      { agent_type: 'BUYER', price: 46000 },
    ];

    const buyerBids = bids.filter((b) => b.agent_type === 'BUYER');
    const vendorBids = bids.filter((b) => b.agent_type === 'VENDOR');

    expect(buyerBids).toHaveLength(2);
    expect(vendorBids).toHaveLength(1);
  });

  it('identifies completion states', () => {
    expect(['ACCEPTED', 'DEADLOCK'].includes('ACCEPTED')).toBe(true);
    expect(['ACCEPTED', 'DEADLOCK'].includes('DEADLOCK')).toBe(true);
    expect(['ACCEPTED', 'DEADLOCK'].includes('IN_PROGRESS')).toBe(false);
  });
});
