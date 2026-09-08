import type { ContractDetails } from '@/types/contract';

interface ContractSummaryProps {
  contract: ContractDetails;
}

export function ContractSummary({ contract }: ContractSummaryProps) {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || '';
  const pdfUrl = `${baseUrl}/api/v1/contract/${contract.session_id}/pdf`;

  return (
    <div className="max-w-2xl mx-auto px-4 py-6 space-y-6">

      {/* Victory banner */}
      <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-5 text-center">
        <p className="text-4xl mb-2">🎉</p>
        <h2 className="text-xl font-bold text-emerald-800">Deal Reached!</h2>
        <p className="text-sm text-emerald-600 mt-1">
          Both parties reached consensus. The contract has been generated and
          logged to the AIMS governance audit trail.
        </p>
      </div>

      {/* Agreed terms */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="bg-gray-50 border-b border-gray-200 px-5 py-3 flex items-center gap-2">
          <span className="text-sm font-bold text-gray-800">📋 Agreed Commercial Terms</span>
        </div>
        <div className="grid grid-cols-3 divide-x divide-gray-100">
          <div className="py-5 px-4 text-center">
            <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">Final Price</p>
            <p className="text-2xl font-black text-emerald-700">
              ${contract.final_price.toLocaleString()}
            </p>
          </div>
          <div className="py-5 px-4 text-center">
            <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">Delivery</p>
            <p className="text-2xl font-black text-blue-700">
              {contract.final_delivery_days}
              <span className="text-base font-semibold"> days</span>
            </p>
          </div>
          <div className="py-5 px-4 text-center">
            <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">SLA Penalty</p>
            <p className="text-2xl font-black text-orange-700">
              {contract.final_sla_percent}
              <span className="text-base font-semibold">%</span>
            </p>
          </div>
        </div>
      </div>

      {/* Governance metadata */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 space-y-3">
        <h3 className="text-sm font-bold text-gray-800 flex items-center gap-2">
          🛡️ AIMS Governance Record
        </h3>
        <div className="grid grid-cols-2 gap-3 text-xs text-gray-600">
          <div>
            <p className="text-gray-400 mb-0.5">Session ID</p>
            <p className="font-mono bg-gray-50 px-2 py-1 rounded text-gray-700 break-all">
              {contract.session_id}
            </p>
          </div>
          <div>
            <p className="text-gray-400 mb-0.5">Executed At</p>
            <p className="font-mono bg-gray-50 px-2 py-1 rounded text-gray-700">
              {new Date(contract.created_at).toLocaleString()}
            </p>
          </div>
        </div>
        <p className="text-[11px] text-gray-400 pt-1">
          All negotiation bids were validated by the Safe AI Arbiter and written
          to <code className="bg-gray-100 px-1 rounded">aims_audit_trail.jsonl</code> in real time.
        </p>
      </div>

      {/* PDF download */}
      <a
        href={pdfUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="flex items-center justify-center gap-3 w-full bg-blue-600 text-white py-3.5 rounded-xl font-bold text-base hover:bg-blue-700 transition-colors shadow-sm"
      >
        <span className="text-xl">📄</span>
        Download PDF Contract
      </a>
    </div>
  );
}
