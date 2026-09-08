import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { App } from '@/App';
import { negotiationApi } from '@/api/negotiationApi';

function renderWithProviders(route = '/') {
  const store = configureStore({
    reducer: {
      [negotiationApi.reducerPath]: negotiationApi.reducer,
    },
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware().concat(negotiationApi.middleware),
  });
  return render(
    <Provider store={store}>
      <MemoryRouter initialEntries={[route]}>
        <App />
      </MemoryRouter>
    </Provider>
  );
}

describe('Full navigation flow', () => {
  it('home page has all form elements', () => {
    renderWithProviders('/');
    expect(screen.getByText('Max Budget ($)')).toBeInTheDocument();
    expect(screen.getByText('Min Price ($)')).toBeInTheDocument();
    expect(screen.getByText('Max Rounds')).toBeInTheDocument();
  });

  it('arena page renders', () => {
    renderWithProviders('/arena/test');
    const hasArena = screen.queryByText('Negotiation Arena');
    const hasLoading = screen.queryByText(/loading negotiation/i);
    expect(hasArena || hasLoading).toBeTruthy();
  });

  it('contract page renders loading or error', () => {
    renderWithProviders('/contract/test');
    const hasLoading = screen.queryByText(/loading contract/i);
    const hasError = screen.queryByText('Contract not found');
    expect(hasLoading || hasError).toBeTruthy();
  });
});
