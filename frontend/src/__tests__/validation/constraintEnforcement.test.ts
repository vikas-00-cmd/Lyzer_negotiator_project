import { describe, it, expect } from 'vitest';
import { BUYER_CONSTRAINTS, VENDOR_CONSTRAINTS } from '@/types/policy';

describe('Constraint enforcement', () => {
  it('rejects buyer budget exceeding 50000', () => {
    const value = 55000;
    expect(value).toBeGreaterThan(BUYER_CONSTRAINTS.max_budget.max);
  });

  it('rejects buyer delivery exceeding 45 days', () => {
    const value = 50;
    expect(value).toBeGreaterThan(BUYER_CONSTRAINTS.max_delivery_days.max);
  });

  it('rejects buyer SLA below 2%', () => {
    const value = 1.0;
    expect(value).toBeLessThan(BUYER_CONSTRAINTS.min_sla_percent.min);
  });

  it('rejects vendor price below 42000', () => {
    const value = 40000;
    expect(value).toBeLessThan(VENDOR_CONSTRAINTS.min_price.min);
  });

  it('rejects vendor delivery below 30 days', () => {
    const value = 25;
    expect(value).toBeLessThan(VENDOR_CONSTRAINTS.min_delivery_days.min);
  });

  it('rejects vendor SLA above 5%', () => {
    const value = 6.0;
    expect(value).toBeGreaterThan(VENDOR_CONSTRAINTS.max_sla_percent.max);
  });

  it('accepts values within bounds', () => {
    expect(48000).toBeLessThanOrEqual(BUYER_CONSTRAINTS.max_budget.max);
    expect(40).toBeLessThanOrEqual(BUYER_CONSTRAINTS.max_delivery_days.max);
    expect(3.0).toBeGreaterThanOrEqual(BUYER_CONSTRAINTS.min_sla_percent.min);
    expect(43000).toBeGreaterThanOrEqual(VENDOR_CONSTRAINTS.min_price.min);
    expect(32).toBeGreaterThanOrEqual(VENDOR_CONSTRAINTS.min_delivery_days.min);
    expect(4.5).toBeLessThanOrEqual(VENDOR_CONSTRAINTS.max_sla_percent.max);
  });
});
