import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { PolicyForm } from '@/components/PolicyForm';
import { negotiationApi } from '@/api/negotiationApi';

function renderWithProviders(ui: React.ReactElement) {
  const store = configureStore({
    reducer: {
      [negotiationApi.reducerPath]: negotiationApi.reducer,
    },
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware().concat(negotiationApi.middleware),
  });
  return render(<Provider store={store}>{ui}</Provider>);
}

describe('PolicyForm', () => {
  it('renders form fields', () => {
    renderWithProviders(<PolicyForm onSuccess={vi.fn()} />);
    expect(screen.getByText('Max Budget ($)')).toBeInTheDocument();
    expect(screen.getByText('Min Price ($)')).toBeInTheDocument();
    expect(screen.getByText('Start Negotiation')).toBeInTheDocument();
  });

  it('has default values', () => {
    renderWithProviders(<PolicyForm onSuccess={vi.fn()} />);
    const budgetInput = screen.getByDisplayValue('50000') as HTMLInputElement;
    expect(budgetInput).toBeInTheDocument();
  });
});
