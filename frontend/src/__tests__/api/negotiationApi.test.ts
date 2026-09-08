import { describe, it, expect } from 'vitest';
import { negotiationApi } from '@/api/negotiationApi';

describe('negotiationApi', () => {
  it('has correct reducer path', () => {
    expect(negotiationApi.reducerPath).toBe('negotiationApi');
  });

  it('has all required endpoints', () => {
    const endpoints = negotiationApi.endpoints;
    expect(endpoints.startNegotiation).toBeDefined();
    expect(endpoints.getNegotiationStatus).toBeDefined();
    expect(endpoints.autoNegotiate).toBeDefined();
    expect(endpoints.stepNegotiation).toBeDefined();
    expect(endpoints.getRounds).toBeDefined();
    expect(endpoints.getContractDetails).toBeDefined();
  });
});
