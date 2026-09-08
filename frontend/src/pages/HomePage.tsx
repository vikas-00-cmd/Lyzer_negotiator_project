import { useNavigate } from 'react-router-dom';
import { PolicyForm } from '@/components/PolicyForm';

export function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <header className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🤝</span>
            <h1 className="text-xl font-black text-slate-800 tracking-tight">
              Lyzr<span className="text-blue-600">Negotiate</span>
            </h1>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/history')}
              className="font-bold text-slate-700 border-2 border-slate-200 rounded-lg px-4 py-1.5 hover:bg-slate-50 hover:border-slate-300 shadow-sm transition-all duration-200"
            >
              Negotiation History
            </button>
            <span className="bg-blue-50 text-blue-700 text-xs font-bold px-3 py-1 rounded-full border border-blue-200">
              Hackathon Demo
            </span>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-7xl mx-auto px-6 py-12 grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">
        {/* Left Column: Hero & Value Prop */}
        <div className="lg:col-span-5 space-y-8 pt-8">
          <div>
            <h2 className="text-4xl font-black text-slate-900 leading-tight mb-4">
              Autonomous B2B <br />
              <span className="text-blue-600">Supply Chain Negotiations</span>
            </h2>
            <p className="text-lg text-slate-600 leading-relaxed">
              Powered by the official <strong className="text-slate-800">Lyzr Agent Studio API</strong>. 
              Define your strict procurement boundaries and let bounded AI agents negotiate price, 
              delivery, and SLA terms automatically.
            </p>
          </div>

          <div className="space-y-4">
            <div className="flex gap-4">
              <div className="text-2xl">🛡️</div>
              <div>
                <h3 className="font-bold text-slate-900">Safe AI Arbiter Guardrails</h3>
                <p className="text-sm text-slate-600">Every bid is mathematically validated against walk-away policies before being transmitted.</p>
              </div>
            </div>
            <div className="flex gap-4">
              <div className="text-2xl">⚖️</div>
              <div>
                <h3 className="font-bold text-slate-900">AIMS Governance</h3>
                <p className="text-sm text-slate-600">Tamper-proof JSONL audit trails log every concession and justification.</p>
              </div>
            </div>
            <div className="flex gap-4">
              <div className="text-2xl">📄</div>
              <div>
                <h3 className="font-bold text-slate-900">Automated Contracting</h3>
                <p className="text-sm text-slate-600">Reaching consensus instantly generates a production-grade PDF agreement.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Policy Form */}
        <div className="lg:col-span-7 bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
          <PolicyForm onSuccess={(id) => navigate(`/arena/${id}`)} />
        </div>
      </main>
    </div>
  );
}
