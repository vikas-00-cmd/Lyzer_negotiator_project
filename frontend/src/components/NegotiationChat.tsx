import { useEffect, useRef } from 'react';
import type { ProposalBid } from '@/types/proposal';
import { ProposalAction } from '@/types/proposal';

interface NegotiationChatProps {
  bids: ProposalBid[];
}

export function NegotiationChat({ bids }: NegotiationChatProps) {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [bids]);

  return (
    <div className="flex flex-col h-full bg-white rounded-xl border border-gray-200 shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
        <h3 className="text-sm font-bold text-gray-800">Negotiation Log</h3>
        <span className="text-xs text-gray-400">{bids.length} bids exchanged</span>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-3 p-4">
        {bids.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center py-12">
            <span className="text-4xl mb-3">🤝</span>
            <p className="text-gray-400 text-sm">No bids yet.</p>
            <p className="text-gray-300 text-xs mt-1">Use the controls below to begin.</p>
          </div>
        )}
        {bids.map((bid, i) => (
          <ChatBubble key={i} bid={bid} />
        ))}
        <div ref={endRef} />
      </div>
    </div>
  );
}

function ChatBubble({ bid }: { bid: ProposalBid }) {
  const isBuyer = bid.agent_type === 'BUYER';
  const isAccept = bid.action === ProposalAction.ACCEPT;
  const isEnd = bid.action === ProposalAction.END_NEGOTIATION;

  // Bubble colour
  const bubbleCls = isAccept
    ? 'bg-emerald-50 border-emerald-300'
    : isEnd
    ? 'bg-red-50 border-red-300'
    : isBuyer
    ? 'bg-blue-50 border-blue-200'
    : 'bg-green-50 border-green-200';

  const align = isBuyer ? 'mr-auto' : 'ml-auto';
  const agentColor = isBuyer ? 'text-blue-700 bg-blue-100' : 'text-green-700 bg-green-100';

  // Action badge style
  const actionCls = isAccept
    ? 'bg-emerald-200 text-emerald-800'
    : isEnd
    ? 'bg-red-200 text-red-800'
    : 'bg-gray-200 text-gray-600';

  return (
    <div className={`max-w-[82%] ${align}`}>
      <div className={`${bubbleCls} border rounded-xl p-3 shadow-sm`}>

        {/* Top row: agent | round | action | Safe AI badge */}
        <div className="flex items-center gap-1.5 mb-2 flex-wrap">
          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${agentColor}`}>
            {bid.agent_type}
          </span>
          <span className="text-[10px] text-gray-400">Round {bid.round_number}</span>
          <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${actionCls}`}>
            {bid.action}
          </span>
          {/* Safe AI validation badge — always shown after arbiter passes */}
          {!isEnd && (
            <span className="ml-auto flex items-center gap-1 text-[10px] text-emerald-700 bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 rounded-full font-medium">
              🛡️ Safe AI ✓
            </span>
          )}
        </div>

        {/* Bid values */}
        <div className="flex items-center gap-2 text-sm font-medium text-gray-800 flex-wrap">
          <span className="font-mono">${bid.price.toLocaleString()}</span>
          <span className="text-gray-300">|</span>
          <span>{bid.delivery_days} days</span>
          <span className="text-gray-300">|</span>
          <span>{bid.sla_percent}% SLA</span>
        </div>

        {/* Justification */}
        {bid.justification && (
          <p className="text-[11px] text-gray-500 mt-1.5 italic leading-relaxed">
            "{bid.justification}"
          </p>
        )}

        {/* Accept celebration */}
        {isAccept && (
          <p className="mt-2 text-xs font-bold text-emerald-700">
            ✅ Deal accepted — proceeding to contract generation
          </p>
        )}
      </div>
    </div>
  );
}
