import { describe, it, expect } from 'vitest';
import { negotiationApi, type StartRequest } from '@/api/negotiationApi';

describe('API integration types', () => {
  it('StartRequest has all required fields', () => {
    const request: StartRequest = {
      buyer_max_budget: 50000,
      buyer_max_delivery_days: 45,
      buyer_min_sla_percent: 2.0,
      vendor_min_price: 42000,
      vendor_min_delivery_days: 30,
      vendor_max_sla_percent: 5.0,
    };

    expect(request.buyer_max_budget).toBeGreaterThan(0);
    expect(request.vendor_min_price).toBeGreaterThan(0);
  });

  it('api has correct reducer path', () => {
    expect(negotiationApi.reducerPath).toBe('negotiationApi');
  });

  it('api has correct endpoints', () => {
    expect(negotiationApi.endpoints.startNegotiation).toBeDefined();
    expect(negotiationApi.endpoints.getNegotiationStatus).toBeDefined();
    expect(negotiationApi.endpoints.autoNegotiate).toBeDefined();
    expect(negotiationApi.endpoints.stepNegotiation).toBeDefined();
    expect(negotiationApi.endpoints.getRounds).toBeDefined();
    expect(negotiationApi.endpoints.getContractDetails).toBeDefined();
  });
});
