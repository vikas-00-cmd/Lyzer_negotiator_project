import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { ProposalBid } from '@/types/proposal';

interface ConcessionChartProps {
  bids: ProposalBid[];
}

export function ConcessionChart({ bids }: ConcessionChartProps) {
  const chartData = bids.map((bid) => ({
    round: `R${bid.round_number}-${bid.agent_type.slice(0, 1)}`,
    price: bid.price,
    delivery_days: bid.delivery_days,
    sla_percent: bid.sla_percent,
    agent: bid.agent_type,
  }));

  const buyerData = chartData.filter((d) => d.agent === 'BUYER');
  const vendorData = chartData.filter((d) => d.agent === 'VENDOR');

  const mergedData = buyerData.map((b, i) => ({
    round: b.round,
    buyerPrice: b.price,
    vendorPrice: vendorData[i]?.price ?? null,
    buyerDelivery: b.delivery_days,
    vendorDelivery: vendorData[i]?.delivery_days ?? null,
    buyerSla: b.sla_percent,
    vendorSla: vendorData[i]?.sla_percent ?? null,
  }));

  if (bids.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg">
        <p className="text-gray-400">Waiting for negotiation data...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold">Concession Curves</h3>

      <div>
        <p className="text-sm text-gray-500 mb-2">Price ($)</p>
        <ResponsiveContainer width="100%" height={150}>
          <LineChart data={mergedData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="round" fontSize={12} />
            <YAxis fontSize={12} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="buyerPrice" name="Buyer" stroke="#3b82f6" strokeWidth={2} dot={{ r: 4 }} />
            <Line type="monotone" dataKey="vendorPrice" name="Vendor" stroke="#22c55e" strokeWidth={2} dot={{ r: 4 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div>
        <p className="text-sm text-gray-500 mb-2">Delivery (days)</p>
        <ResponsiveContainer width="100%" height={150}>
          <LineChart data={mergedData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="round" fontSize={12} />
            <YAxis fontSize={12} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="buyerDelivery" name="Buyer" stroke="#3b82f6" strokeWidth={2} dot={{ r: 4 }} />
            <Line type="monotone" dataKey="vendorDelivery" name="Vendor" stroke="#22c55e" strokeWidth={2} dot={{ r: 4 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div>
        <p className="text-sm text-gray-500 mb-2">SLA Penalty (%)</p>
        <ResponsiveContainer width="100%" height={150}>
          <LineChart data={mergedData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="round" fontSize={12} />
            <YAxis fontSize={12} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="buyerSla" name="Buyer" stroke="#3b82f6" strokeWidth={2} dot={{ r: 4 }} />
            <Line type="monotone" dataKey="vendorSla" name="Vendor" stroke="#22c55e" strokeWidth={2} dot={{ r: 4 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
