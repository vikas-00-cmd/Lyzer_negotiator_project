import { useNavigate } from 'react-router-dom';
import { useGetSessionsQuery } from '@/api/negotiationApi';
import { StatusBadge } from '@/components/StatusBadge';

export function HistoryPage() {
  const navigate = useNavigate();
  const { data: sessions, isLoading } = useGetSessionsQuery(undefined, {
    refetchOnMountOrArgChange: true,
  });

  const baseUrl = import.meta.env.VITE_API_BASE_URL || '';

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  // Handle Empty State as requested
  if (!sessions || sessions.length === 0) {
    return (
      <div className="min-h-screen flex flex-col bg-gray-50">
        <header className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-10">
          <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-3 cursor-pointer" onClick={() => navigate('/')}>
              <span className="text-2xl">🤝</span>
              <h1 className="text-xl font-black text-slate-800 tracking-tight">
                Lyzr<span className="text-blue-600">Negotiate</span>
              </h1>
            </div>
          </div>
        </header>

        <main className="flex-1 max-w-4xl mx-auto px-6 py-20 w-full text-center">
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-12">
            <div className="text-5xl mb-4">📭</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">No negotiations recorded yet</h2>
            <p className="text-gray-500 mb-8 max-w-md mx-auto">
              You haven't run any AI negotiations. Head back to the setup form to define your policies and start your first session.
            </p>
            <button
              onClick={() => navigate('/')}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg font-bold hover:bg-blue-700 transition-colors"
            >
              Start First Negotiation
            </button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <header className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => navigate('/')}>
            <span className="text-2xl">🤝</span>
            <h1 className="text-xl font-black text-slate-800 tracking-tight">
              Lyzr<span className="text-blue-600">Negotiate</span>
            </h1>
          </div>
          <button
            onClick={() => navigate('/')}
            className="text-sm font-semibold text-blue-600 hover:text-blue-800 transition-colors"
          >
            + New Negotiation
          </button>
        </div>
      </header>

      <main className="flex-1 max-w-6xl mx-auto px-6 py-12 w-full">
        {/* NEW: Global Back Button */}
        <button 
          onClick={() => navigate('/')} 
          className="flex items-center text-slate-500 hover:text-slate-800 font-bold mb-6 transition-colors duration-200"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to Setup
        </button>

        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Negotiation History</h2>
            <p className="text-gray-500 text-sm mt-1">Review past sessions and download final contracts.</p>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-200 text-xs uppercase tracking-wider text-gray-500 font-semibold">
                  <th className="px-6 py-4">Date</th>
                  <th className="px-6 py-4">Session ID</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Rounds</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {sessions.map((session) => {
                  const dateStr = session.created_at
                    ? new Date(session.created_at).toLocaleString()
                    : 'Unknown';

                  return (
                    <tr key={session.id} className="hover:bg-slate-50 transition-colors">
                      <td className="px-6 py-4 text-sm text-gray-600">{dateStr}</td>
                      <td className="px-6 py-4">
                        <span className="font-mono text-xs bg-slate-100 text-slate-600 px-2 py-1 rounded">
                          {session.id.slice(0, 8)}...
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <StatusBadge status={session.status} />
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {session.current_round} / {session.max_rounds}
                      </td>
                      <td className="px-6 py-4 text-right space-x-2">
                        <button
                          onClick={() => navigate(`/arena/${session.id}`)}
                          className="inline-flex items-center text-sm font-semibold text-blue-600 hover:bg-blue-50 px-3 py-1.5 rounded-md transition-colors"
                        >
                          View Arena
                        </button>
                        {session.status === 'ACCEPTED' && (
                          <a
                            href={`${baseUrl}/api/v1/contract/${session.id}/pdf`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 text-sm font-semibold text-emerald-600 hover:bg-emerald-50 px-3 py-1.5 rounded-md transition-colors"
                          >
                            <span>📄</span> PDF
                          </a>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}
