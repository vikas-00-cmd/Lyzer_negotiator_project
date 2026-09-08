import { describe, it, expect } from 'vitest';
import { ProposalAction } from '@/types/proposal';

describe('ProposalAction enum', () => {
  it('has correct values', () => {
    expect(ProposalAction.OFFER).toBe('OFFER');
    expect(ProposalAction.ACCEPT).toBe('ACCEPT');
    expect(ProposalAction.END_NEGOTIATION).toBe('END_NEGOTIATION');
  });

  it('has exactly 3 members', () => {
    expect(Object.keys(ProposalAction)).toHaveLength(3);
  });
});
