import { describe, it, expect } from 'vitest';
import type { ContractDetails } from '@/types/contract';

describe('ContractDetails interface', () => {
  it('has all required fields', () => {
    const contract: ContractDetails = {
      id: 'test-id',
      session_id: 'session-id',
      final_price: 45000,
      final_delivery_days: 30,
      final_sla_percent: 3.5,
      pdf_file_path: './contracts/test.pdf',
      created_at: '2024-01-01T00:00:00Z',
    };

    expect(contract.id).toBeDefined();
    expect(contract.session_id).toBeDefined();
    expect(contract.final_price).toBeGreaterThan(0);
    expect(contract.final_delivery_days).toBeGreaterThan(0);
    expect(contract.final_sla_percent).toBeGreaterThan(0);
    expect(contract.created_at).toBeDefined();
  });
});
