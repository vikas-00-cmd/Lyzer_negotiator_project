import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { App } from '@/App';
import { negotiationApi } from '@/api/negotiationApi';

function renderWithProviders(ui: React.ReactElement, route = '/') {
  const store = configureStore({
    reducer: {
      [negotiationApi.reducerPath]: negotiationApi.reducer,
    },
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware().concat(negotiationApi.middleware),
  });
  return render(
    <Provider store={store}>
      <MemoryRouter initialEntries={[route]}>{ui}</MemoryRouter>
    </Provider>
  );
}

describe('App routes', () => {
  it('renders HomePage on /', () => {
    renderWithProviders(<App />);
    expect(screen.getByText(/policy setup/i)).toBeInTheDocument();
  });

  it('renders arena route', () => {
    renderWithProviders(<App />, '/arena/test-id');
    // ArenaPage shows loading when no backend
    expect(screen.getByText(/loading negotiation/i)).toBeInTheDocument();
  });
});
