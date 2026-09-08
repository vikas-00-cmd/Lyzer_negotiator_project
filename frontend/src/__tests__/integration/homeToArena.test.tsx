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

describe('Home to Arena flow', () => {
  it('renders policy form on home page', () => {
    renderWithProviders('/');
    expect(screen.getByText(/policy setup/i)).toBeInTheDocument();
    expect(screen.getByText('Max Budget ($)')).toBeInTheDocument();
  });

  it('has start negotiation button', () => {
    renderWithProviders('/');
    expect(screen.getByRole('button', { name: /start negotiation/i })).toBeInTheDocument();
  });
});
