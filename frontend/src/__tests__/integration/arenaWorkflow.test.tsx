import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { ArenaPage } from '@/pages/ArenaPage';
import { negotiationApi } from '@/api/negotiationApi';

function renderArena(sessionId = 'test-session') {
  const store = configureStore({
    reducer: {
      [negotiationApi.reducerPath]: negotiationApi.reducer,
    },
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware().concat(negotiationApi.middleware),
  });
  return render(
    <Provider store={store}>
      <MemoryRouter initialEntries={[`/arena/${sessionId}`]}>
        <ArenaPage />
      </MemoryRouter>
    </Provider>
  );
}

describe('ArenaPage', () => {
  it('renders arena structure', () => {
    renderArena();
    expect(screen.getByText('Negotiation Arena')).toBeInTheDocument();
    expect(screen.getByText('Negotiation Log')).toBeInTheDocument();
    expect(screen.getByText('Waiting for negotiation data...')).toBeInTheDocument();
    expect(screen.getByText(/New Negotiation/)).toBeInTheDocument();
  });
});
