import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { RoundTimeline } from '@/components/RoundTimeline';

describe('RoundTimeline', () => {
  it('displays current round', () => {
    render(<RoundTimeline currentRound={3} maxRounds={10} />);
    expect(screen.getByText('30%')).toBeInTheDocument();
  });

  it('calculates percentage', () => {
    render(<RoundTimeline currentRound={5} maxRounds={10} />);
    expect(screen.getByText('50%')).toBeInTheDocument();
  });
});
