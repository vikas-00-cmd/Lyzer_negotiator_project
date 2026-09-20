import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ContractSummary } from '@/components/ContractSummary';
import type { ContractDetails } from '@/types/contract';

const mockContract: ContractDetails = {
  id: 'contract-1',
  session_id: 'session-1',
  final_price: 45500,
  final_delivery_days: 35,
  final_sla_percent: 3.5,
  pdf_file_path: './contracts/test.pdf',
  created_at: '2024-01-01T00:00:00Z',
};

describe('ContractSummary', () => {
  it('renders contract terms', () => {
    render(<ContractSummary contract={mockContract} />);
    expect(screen.getByText(/\$45,500/)).toBeInTheDocument();
    expect(screen.getByText(/35/)).toBeInTheDocument();
    expect(screen.getByText(/days/)).toBeInTheDocument();
    expect(screen.getByText(/3\.5/)).toBeInTheDocument();
    expect(screen.getByText(/%/)).toBeInTheDocument();
  });

  it('has PDF download link', () => {
    render(<ContractSummary contract={mockContract} />);
    const link = screen.getByText('Download PDF Contract');
    expect(link).toHaveAttribute('href', '/api/v1/contract/session-1/pdf');
  });
});
