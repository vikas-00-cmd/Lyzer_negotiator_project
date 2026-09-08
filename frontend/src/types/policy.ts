export interface BuyerPolicyEnvelope {
  max_budget: number;
  max_delivery_days: number;
  min_sla_percent: number;
}

export interface VendorPolicyEnvelope {
  min_price: number;
  min_delivery_days: number;
  max_sla_percent: number;
}

export interface NegotiationPolicies {
  buyer: BuyerPolicyEnvelope;
  vendor: VendorPolicyEnvelope;
}

export const BUYER_CONSTRAINTS = {
  max_budget: { min: 1, max: 50000 },
  max_delivery_days: { min: 1, max: 45 },
  min_sla_percent: { min: 2.0, max: 100 },
} as const;

export const VENDOR_CONSTRAINTS = {
  min_price: { min: 42000, max: 1000000 },
  min_delivery_days: { min: 30, max: 365 },
  max_sla_percent: { min: 0.1, max: 5.0 },
} as const;
