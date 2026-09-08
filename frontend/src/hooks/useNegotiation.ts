import { useMemo } from 'react';
import {
  useGetNegotiationStatusQuery,
  useGetRoundsQuery,
} from '@/api/negotiationApi';
import type { ProposalBid } from '@/types/proposal';

export function useNegotiation(sessionId: string | null) {
  const {
    data: session,
    isLoading: sessionLoading,
    isFetching: sessionFetching,
  } = useGetNegotiationStatusQuery(sessionId!, {
    skip: !sessionId,
  });

  const {
    data: rounds,
    isLoading: roundsLoading,
  } = useGetRoundsQuery(sessionId!, {
    skip: !sessionId,
  });

  const isActive = session?.status === 'IN_PROGRESS';
  const isAccepted = session?.status === 'ACCEPTED';
  const isDeadlock = session?.status === 'DEADLOCK';
  const isPending = session?.status === 'PENDING';
  const isComplete = isAccepted || isDeadlock;

  const currentBids: ProposalBid[] = useMemo(() => {
    if (!rounds) return [];
    return rounds.map((r) => ({
      price: r.price,
      delivery_days: r.delivery_days,
      sla_percent: r.sla_percent,
      action: r.action as ProposalBid['action'],
      justification: r.justification,
      round_number: r.round_number,
      agent_type: r.agent_type as 'BUYER' | 'VENDOR',
    }));
  }, [rounds]);

  const buyerBids = currentBids.filter((b) => b.agent_type === 'BUYER');
  const vendorBids = currentBids.filter((b) => b.agent_type === 'VENDOR');

  return {
    session,
    rounds: currentBids,
    buyerBids,
    vendorBids,
    isLoading: sessionLoading || roundsLoading,
    isPolling: sessionFetching && !sessionLoading,
    isActive,
    isAccepted,
    isDeadlock,
    isPending,
    isComplete,
    currentRound: session?.current_round ?? 0,
    maxRounds: session?.max_rounds ?? 10,
    status: session?.status ?? 'IDLE',
  };
}
