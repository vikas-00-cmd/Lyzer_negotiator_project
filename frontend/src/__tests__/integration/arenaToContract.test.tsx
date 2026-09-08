import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { ContractPage } from '@/pages/ContractPage';
import { negotiationApi } from '@/api/negotiationApi';

function renderContract(sessionId = 'test-session') {
  const store = configureStore({
    reducer: {
      [negotiationApi.reducerPath]: negotiationApi.reducer,
    },
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware().concat(negotiationApi.middleware),
  });
  return render(
    <Provider store={store}>
      <MemoryRouter initialEntries={[`/contract/${sessionId}`]}>
        <ContractPage />
      </MemoryRouter>
    </Provider>
  );
}

describe('ContractPage', () => {
  it('shows error state when no backend', () => {
    renderContract();
    expect(screen.getByText('Contract not found')).toBeInTheDocument();
  });

  it('has start new negotiation link when not found', () => {
    renderContract();
    expect(screen.getByText('Start New Negotiation')).toBeInTheDocument();
  });
});
