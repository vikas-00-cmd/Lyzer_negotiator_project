import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { StatusBadge } from '@/components/StatusBadge';

describe('StatusBadge', () => {
  it('renders Pending status', () => {
    render(<StatusBadge status="PENDING" />);
    expect(screen.getByText('Pending')).toBeInTheDocument();
  });

  it('renders Accepted status', () => {
    render(<StatusBadge status="ACCEPTED" />);
    expect(screen.getByText('Accepted')).toBeInTheDocument();
  });

  it('renders Deadlock status', () => {
    render(<StatusBadge status="DEADLOCK" />);
    expect(screen.getByText('Deadlock')).toBeInTheDocument();
  });

  it('shows pulse animation for IN_PROGRESS', () => {
    render(<StatusBadge status="IN_PROGRESS" />);
    const pulse = document.querySelector('.animate-pulse');
    expect(pulse).toBeInTheDocument();
  });
});
