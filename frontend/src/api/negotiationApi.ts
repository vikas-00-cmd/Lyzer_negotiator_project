import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import type { BuyerPolicyEnvelope, VendorPolicyEnvelope } from '@/types/policy';
import type { RoundResponse } from '@/types/proposal';
import type { ContractDetails } from '@/types/contract';

export interface SessionResponse {
  id: string;
  status: string;
  current_round: number;
  max_rounds: number;
  buyer_policy: BuyerPolicyEnvelope;
  vendor_policy: VendorPolicyEnvelope;
  created_at?: string;
}

export interface StepResponse {
  session_id: string;
  current_round: number;
  is_complete: boolean;
  history: Array<{
    price: number;
    delivery_days: number;
    sla_percent: number;
    action: string;
    justification: string;
    round_number: number;
    agent_type: string;
  }>;
  consensus: {
    price: number;
    delivery_days: number;
    sla_percent: number;
  } | null;
}

export interface StartRequest {
  buyer_max_budget: number;
  buyer_max_delivery_days: number;
  buyer_min_sla_percent: number;
  vendor_min_price: number;
  vendor_min_delivery_days: number;
  vendor_max_sla_percent: number;
  max_rounds?: number;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

export const negotiationApi = createApi({
  reducerPath: 'negotiationApi',
  baseQuery: fetchBaseQuery({ baseUrl: `${API_BASE}/api/v1` }),
  tagTypes: ['Session', 'Rounds', 'Contract'],
  endpoints: (builder) => ({
    getSessions: builder.query<SessionResponse[], void>({
      query: () => '/negotiation/sessions',
      providesTags: ['Session'],
    }),
    startNegotiation: builder.mutation<SessionResponse, StartRequest>({
      query: (body) => ({
        url: '/negotiation/start',
        method: 'POST',
        body,
      }),
      invalidatesTags: ['Session'],
    }),

    getNegotiationStatus: builder.query<SessionResponse, string>({
      query: (id) => `/negotiation/${id}/status`,
      providesTags: ['Session'],
    }),

    autoNegotiate: builder.mutation<SessionResponse, string>({
      query: (id) => ({
        url: `/negotiation/${id}/auto`,
        method: 'POST',
      }),
      invalidatesTags: ['Session', 'Rounds', 'Contract'],
    }),

    stepNegotiation: builder.mutation<StepResponse, string>({
      query: (id) => ({
        url: `/negotiation/${id}/step`,
        method: 'POST',
      }),
      invalidatesTags: ['Session', 'Rounds'],
    }),

    getRounds: builder.query<RoundResponse[], string>({
      query: (id) => `/negotiation/${id}/rounds`,
      providesTags: ['Rounds'],
    }),

    getContractDetails: builder.query<ContractDetails, string>({
      query: (id) => `/contract/${id}/details`,
      providesTags: ['Contract'],
    }),
  }),
});

export const {
  useGetSessionsQuery,
  useStartNegotiationMutation,
  useGetNegotiationStatusQuery,
  useAutoNegotiateMutation,
  useStepNegotiationMutation,
  useGetRoundsQuery,
  useGetContractDetailsQuery,
} = negotiationApi;
