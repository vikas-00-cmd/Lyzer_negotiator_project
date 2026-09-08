import { useParams, useNavigate } from 'react-router-dom';
import { useGetContractDetailsQuery } from '@/api/negotiationApi';
import { ContractSummary } from '@/components/ContractSummary';

export function ContractPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: contract, isLoading, error } = useGetContractDetailsQuery(id ?? '', {
    skip: !id,
  });

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-500">Loading contract...</p>
      </div>
    );
  }

  if (error || !contract) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4">
        <p className="text-red-500">Contract not found</p>
        <button
          onClick={() => navigate('/')}
          className="text-blue-600 hover:underline"
        >
          Start New Negotiation
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-bold text-gray-900">Contract</h1>
          <button
            onClick={() => navigate(`/arena/${id}`)}
            className="text-blue-600 hover:underline"
          >
            Back to Arena
          </button>
        </div>
      </header>

      <main className="py-8">
        <ContractSummary contract={contract} />
      </main>
    </div>
  );
}
