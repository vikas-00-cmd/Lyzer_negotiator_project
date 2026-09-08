import { describe, it, expect } from 'vitest';
import { BUYER_CONSTRAINTS, VENDOR_CONSTRAINTS } from '@/types/policy';

describe('BuyerPolicyEnvelope constraints', () => {
  it('max_budget has correct bounds', () => {
    expect(BUYER_CONSTRAINTS.max_budget.min).toBe(1);
    expect(BUYER_CONSTRAINTS.max_budget.max).toBe(50000);
  });

  it('max_delivery_days has correct bounds', () => {
    expect(BUYER_CONSTRAINTS.max_delivery_days.min).toBe(1);
    expect(BUYER_CONSTRAINTS.max_delivery_days.max).toBe(45);
  });

  it('min_sla_percent has correct bounds', () => {
    expect(BUYER_CONSTRAINTS.min_sla_percent.min).toBe(2.0);
    expect(BUYER_CONSTRAINTS.min_sla_percent.max).toBe(100);
  });
});

describe('VendorPolicyEnvelope constraints', () => {
  it('min_price has correct bounds', () => {
    expect(VENDOR_CONSTRAINTS.min_price.min).toBe(42000);
  });

  it('min_delivery_days has correct bounds', () => {
    expect(VENDOR_CONSTRAINTS.min_delivery_days.min).toBe(30);
  });

  it('max_sla_percent has correct bounds', () => {
    expect(VENDOR_CONSTRAINTS.max_sla_percent.max).toBe(5.0);
  });
});
