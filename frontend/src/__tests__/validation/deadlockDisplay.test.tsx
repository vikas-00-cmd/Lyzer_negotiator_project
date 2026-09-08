import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { StatusBadge } from '@/components/StatusBadge';

describe('Deadlock display', () => {
  it('renders Deadlock status correctly', () => {
    render(<StatusBadge status="DEADLOCK" />);
    expect(screen.getByText('Deadlock')).toBeInTheDocument();
  });

  it('applies red styling for deadlock', () => {
    render(<StatusBadge status="DEADLOCK" />);
    const badge = screen.getByText('Deadlock');
    expect(badge.className).toContain('bg-red');
  });

  it('shows accepted with green styling', () => {
    render(<StatusBadge status="ACCEPTED" />);
    const badge = screen.getByText('Accepted');
    expect(badge.className).toContain('bg-green');
  });
});
