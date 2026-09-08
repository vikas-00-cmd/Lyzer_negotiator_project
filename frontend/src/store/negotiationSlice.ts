import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface NegotiationUIState {
  sessionId: string | null;
  pollingEnabled: boolean;
  chartMetric: 'price' | 'delivery_days' | 'sla_percent';
}

const initialState: NegotiationUIState = {
  sessionId: null,
  pollingEnabled: false,
  chartMetric: 'price',
};

const negotiationSlice = createSlice({
  name: 'negotiation',
  initialState,
  reducers: {
    setSessionId: (state, action: PayloadAction<string | null>) => {
      state.sessionId = action.payload;
    },
    setPollingEnabled: (state, action: PayloadAction<boolean>) => {
      state.pollingEnabled = action.payload;
    },
    setChartMetric: (state, action: PayloadAction<'price' | 'delivery_days' | 'sla_percent'>) => {
      state.chartMetric = action.payload;
    },
  },
});

export const { setSessionId, setPollingEnabled, setChartMetric } = negotiationSlice.actions;
export default negotiationSlice.reducer;
