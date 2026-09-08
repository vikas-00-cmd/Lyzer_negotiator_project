import { describe, it, expect } from 'vitest';
import negotiationReducer, {
  setSessionId,
  setPollingEnabled,
  setChartMetric,
} from '@/store/negotiationSlice';

describe('negotiationSlice', () => {
  const initialState = {
    sessionId: null,
    pollingEnabled: false,
    chartMetric: 'price' as const,
  };

  it('returns initial state', () => {
    expect(negotiationReducer(undefined, { type: 'unknown' })).toEqual(initialState);
  });

  it('setSessionId updates sessionId', () => {
    const next = negotiationReducer(initialState, setSessionId('abc-123'));
    expect(next.sessionId).toBe('abc-123');
  });

  it('setSessionId can clear sessionId', () => {
    const withSession = { ...initialState, sessionId: 'abc-123' };
    const next = negotiationReducer(withSession, setSessionId(null));
    expect(next.sessionId).toBeNull();
  });

  it('setPollingEnabled updates pollingEnabled', () => {
    const next = negotiationReducer(initialState, setPollingEnabled(true));
    expect(next.pollingEnabled).toBe(true);
  });

  it('setChartMetric updates chartMetric', () => {
    const next = negotiationReducer(initialState, setChartMetric('delivery_days'));
    expect(next.chartMetric).toBe('delivery_days');
  });
});
