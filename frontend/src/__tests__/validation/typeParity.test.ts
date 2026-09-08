import { describe, it, expect } from 'vitest';
import { BUYER_CONSTRAINTS, VENDOR_CONSTRAINTS } from '@/types/policy';

describe('Type parity with backend Pydantic schemas', () => {
  it('BuyerPolicyEnvelope matches backend constraints', () => {
    expect(BUYER_CONSTRAINTS.max_budget.max).toBe(50000);
    expect(BUYER_CONSTRAINTS.max_delivery_days.max).toBe(45);
    expect(BUYER_CONSTRAINTS.min_sla_percent.min).toBe(2.0);
  });

  it('VendorPolicyEnvelope matches backend constraints', () => {
    expect(VENDOR_CONSTRAINTS.min_price.min).toBe(42000);
    expect(VENDOR_CONSTRAINTS.min_delivery_days.min).toBe(30);
    expect(VENDOR_CONSTRAINTS.max_sla_percent.max).toBe(5.0);
  });

  it('buyer constraints overlap with vendor constraints', () => {
    const buyerMax = BUYER_CONSTRAINTS.max_budget.max;
    const vendorMin = VENDOR_CONSTRAINTS.min_price.min;
    expect(buyerMax).toBeGreaterThanOrEqual(vendorMin);
  });
});
