import { useParams, useNavigate } from 'react-router-dom';
import { useNegotiation } from '@/hooks/useNegotiation';
import { useAutoNegotiateMutation, useStepNegotiationMutation } from '@/api/negotiationApi';
import { StatusBadge } from '@/components/StatusBadge';
import { RoundTimeline } from '@/components/RoundTimeline';
import { NegotiationChat } from '@/components/NegotiationChat';
import { ConcessionChart } from '@/components/ConcessionChart';

export function ArenaPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const {
    rounds,
    session,
    isLoading,
    isAccepted,
    isDeadlock,
    isPending,
    isActive,
    currentRound,
    maxRounds,
    status,
  } = useNegotiation(id ?? null);

  const [autoNegotiate, { isLoading: isAutoLoading }] = useAutoNegotiateMutation();
  const [stepNegotiation, { isLoading: isStepLoading }] = useStepNegotiationMutation();

  const handleAuto = async () => {
    if (!id) return;
    await autoNegotiate(id);
  };

  const handleStep = async () => {
    if (!id) return;
    await stepNegotiation(id);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-gray-500 font-medium">Loading negotiation...</p>
        </div>
      </div>
    );
  }

  const lastBid = rounds[rounds.length - 1];
  const buyerPolicy = session?.buyer_policy as Record<string, number> | undefined;
  const vendorPolicy = session?.vendor_policy as Record<string, number> | undefined;

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">

      {/* ── Header ─────────────────────────────────────────────────────── */}
      <header className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/history')}
              className="text-slate-500 hover:text-slate-900 transition-colors p-1.5 rounded-lg hover:bg-slate-100"
              title="Back to History"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
              </svg>
            </button>
            <div>
              <p className="text-xs font-semibold text-blue-600 uppercase tracking-widest mb-0.5">
                Lyzr B2B Negotiation Platform
              </p>
              <h1 className="text-xl font-bold text-gray-900 leading-tight">
                Negotiation Arena
              </h1>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-xs text-gray-400 font-mono hidden sm:block">
              ID: {id?.slice(0, 8)}…
            </span>
            <StatusBadge status={status} />
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto w-full px-6 py-5 flex-1 flex flex-col gap-5">

        {/* ── Round progress bar ──────────────────────────────────────── */}
        <RoundTimeline currentRound={currentRound} maxRounds={maxRounds} />

        {/* ── Main grid ──────────────────────────────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-5 flex-1">

          {/* Chat column */}
          <div className="lg:col-span-3 min-h-[480px]">
            <NegotiationChat bids={rounds} />
          </div>

          {/* Right sidebar */}
          <div className="lg:col-span-2 flex flex-col gap-4">

            {/* Safe AI Arbiter guardrail panel */}
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-base">🛡️</span>
                <h3 className="text-sm font-bold text-gray-800">Safe AI Arbiter — Policy Bounds</h3>
              </div>
              <div className="grid grid-cols-2 gap-3 text-xs">
                {/* Buyer */}
                <div className="bg-blue-50 rounded-lg p-3 border border-blue-100">
                  <p className="font-bold text-blue-700 mb-2">BUYER limits</p>
                  <div className="space-y-1 text-gray-600">
                    <div className="flex justify-between">
                      <span>Max budget</span>
                      <span className="font-mono font-semibold text-blue-800">
                        ${(buyerPolicy?.max_budget ?? 50000).toLocaleString()}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Max delivery</span>
                      <span className="font-mono font-semibold text-blue-800">
                        {buyerPolicy?.max_delivery_days ?? 45} days
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Min SLA</span>
                      <span className="font-mono font-semibold text-blue-800">
                        {buyerPolicy?.min_sla_percent ?? 2}%
                      </span>
                    </div>
                  </div>
                </div>
                {/* Vendor */}
                <div className="bg-green-50 rounded-lg p-3 border border-green-100">
                  <p className="font-bold text-green-700 mb-2">VENDOR limits</p>
                  <div className="space-y-1 text-gray-600">
                    <div className="flex justify-between">
                      <span>Min price</span>
                      <span className="font-mono font-semibold text-green-800">
                        ${(vendorPolicy?.min_price ?? 42000).toLocaleString()}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Min delivery</span>
                      <span className="font-mono font-semibold text-green-800">
                        {vendorPolicy?.min_delivery_days ?? 30} days
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Max SLA</span>
                      <span className="font-mono font-semibold text-green-800">
                        {vendorPolicy?.max_sla_percent ?? 5}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
              <p className="text-[10px] text-gray-400 mt-2 text-center">
                Every bid is mathematically validated before transmission
              </p>
            </div>

            {/* Last validated bid */}
            {lastBid && (
              <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-base">✅</span>
                  <h3 className="text-sm font-bold text-gray-800">Last Validated Bid</h3>
                  <span className={`ml-auto text-[10px] px-2 py-0.5 rounded-full font-semibold ${
                    lastBid.agent_type === 'BUYER'
                      ? 'bg-blue-100 text-blue-700'
                      : 'bg-green-100 text-green-700'
                  }`}>
                    {lastBid.agent_type}
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-2 text-center">
                  <div className="bg-gray-50 rounded-lg py-2">
                    <p className="text-[10px] text-gray-400 mb-0.5">Price</p>
                    <p className="text-sm font-bold text-gray-800">
                      ${lastBid.price.toLocaleString()}
                    </p>
                  </div>
                  <div className="bg-gray-50 rounded-lg py-2">
                    <p className="text-[10px] text-gray-400 mb-0.5">Delivery</p>
                    <p className="text-sm font-bold text-gray-800">{lastBid.delivery_days}d</p>
                  </div>
                  <div className="bg-gray-50 rounded-lg py-2">
                    <p className="text-[10px] text-gray-400 mb-0.5">SLA</p>
                    <p className="text-sm font-bold text-gray-800">{lastBid.sla_percent}%</p>
                  </div>
                </div>
              </div>
            )}

            {/* Concession chart */}
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 flex-1">
              <ConcessionChart bids={rounds} />
            </div>
          </div>
        </div>

        {/* ── Control bar ────────────────────────────────────────────── */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm px-6 py-4 flex items-center gap-3 flex-wrap">

          {/* PENDING: offer both controls */}
          {isPending && (
            <>
              <button
                onClick={handleStep}
                disabled={isStepLoading}
                className="flex items-center gap-2 bg-indigo-600 text-white px-5 py-2.5 rounded-lg font-semibold text-sm hover:bg-indigo-700 disabled:opacity-50 transition-colors"
              >
                {isStepLoading
                  ? <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  : <span>▶</span>}
                Step Once
              </button>
              <button
                onClick={handleAuto}
                disabled={isAutoLoading}
                className="flex items-center gap-2 bg-blue-600 text-white px-5 py-2.5 rounded-lg font-semibold text-sm hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                {isAutoLoading
                  ? <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  : <span>⚡</span>}
                Run Auto-Negotiation
              </button>
            </>
          )}

          {/* IN_PROGRESS: step only */}
          {isActive && (
            <button
              onClick={handleStep}
              disabled={isStepLoading}
              className="flex items-center gap-2 bg-indigo-600 text-white px-5 py-2.5 rounded-lg font-semibold text-sm hover:bg-indigo-700 disabled:opacity-50 transition-colors"
            >
              {isStepLoading
                ? <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                : <span>▶</span>}
              Step Once — Round {currentRound + 1}
            </button>
          )}

          {/* ACCEPTED: navigate to contract */}
          {isAccepted && (
            <button
              onClick={() => navigate(`/contract/${id}`)}
              className="flex items-center gap-2 bg-green-600 text-white px-6 py-2.5 rounded-lg font-bold text-sm hover:bg-green-700 transition-colors"
            >
              <span>📄</span> View Final Contract
            </button>
          )}

          {/* DEADLOCK */}
          {isDeadlock && (
            <span className="flex items-center gap-2 text-red-600 font-semibold text-sm bg-red-50 border border-red-200 px-4 py-2.5 rounded-lg">
              <span>⛔</span> Deadlock — No agreement reached after {maxRounds} rounds
            </span>
          )}

          <button
            onClick={() => navigate('/')}
            className="ml-auto flex items-center gap-2 bg-blue-600 text-white px-6 py-2.5 rounded-lg font-bold text-sm hover:bg-blue-700 transition-colors shadow-sm"
          >
            <span>+</span> New Negotiation
          </button>
        </div>

      </main>
    </div>
  );
}
