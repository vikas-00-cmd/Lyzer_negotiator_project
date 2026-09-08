import { configureStore } from '@reduxjs/toolkit';
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';
import { negotiationApi } from '@/api/negotiationApi';
import negotiationReducer from './negotiationSlice';

export const store = configureStore({
  reducer: {
    [negotiationApi.reducerPath]: negotiationApi.reducer,
    negotiation: negotiationReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(negotiationApi.middleware),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export const useAppDispatch: () => AppDispatch = useDispatch;
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
