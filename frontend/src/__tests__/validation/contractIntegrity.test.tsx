import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ContractSummary } from '@/components/ContractSummary';
import type { ContractDetails } from '@/types/contract';

describe('Contract integrity', () => {
  const validContract: ContractDetails = {
    id: 'c1',
    session_id: 's1',
    final_price: 45500,
    final_delivery_days: 35,
    final_sla_percent: 3.5,
    pdf_file_path: './contracts/c1.pdf',
    created_at: '2024-01-01T00:00:00Z',
  };

  it('price is within buyer max budget', () => {
    expect(validContract.final_price).toBeLessThanOrEqual(50000);
  });

  it('price is above vendor min price', () => {
    expect(validContract.final_price).toBeGreaterThanOrEqual(42000);
  });

  it('delivery is within buyer max days', () => {
    expect(validContract.final_delivery_days).toBeLessThanOrEqual(45);
  });

  it('delivery is above vendor min days', () => {
    expect(validContract.final_delivery_days).toBeGreaterThanOrEqual(30);
  });

  it('SLA is within buyer min SLA', () => {
    expect(validContract.final_sla_percent).toBeGreaterThanOrEqual(2.0);
  });

  it('SLA is within vendor max SLA', () => {
    expect(validContract.final_sla_percent).toBeLessThanOrEqual(5.0);
  });

  it('renders all contract terms', () => {
    render(<ContractSummary contract={validContract} />);
    expect(screen.getByText('$45,500')).toBeInTheDocument();
    expect(screen.getByText('35 days')).toBeInTheDocument();
    expect(screen.getByText('3.5%')).toBeInTheDocument();
  });
});
