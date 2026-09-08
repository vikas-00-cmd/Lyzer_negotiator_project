import { useForm } from 'react-hook-form';
import { useStartNegotiationMutation, type StartRequest } from '@/api/negotiationApi';
import { BUYER_CONSTRAINTS, VENDOR_CONSTRAINTS } from '@/types/policy';

interface PolicyFormProps {
  onSuccess: (sessionId: string) => void;
}

export function PolicyForm({ onSuccess }: PolicyFormProps) {
  const [startNegotiation, { isLoading }] = useStartNegotiationMutation();

  const { register, handleSubmit, formState: { errors } } = useForm<StartRequest>({
    defaultValues: {
      buyer_max_budget: 50000,
      buyer_max_delivery_days: 45,
      buyer_min_sla_percent: 2.0,
      vendor_min_price: 42000,
      vendor_min_delivery_days: 30,
      vendor_max_sla_percent: 5.0,
      max_rounds: 10,
    },
  });

  const onSubmit = async (data: StartRequest) => {
    try {
      const result = await startNegotiation(data).unwrap();
      onSuccess(result.id);
    } catch {
      alert('Failed to start negotiation');
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="max-w-4xl mx-auto p-6">
      <h2 className="text-2xl font-bold mb-6">Policy Setup</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-blue-50 p-6 rounded-lg">
          <h3 className="text-lg font-semibold text-blue-700 mb-4">Buyer Policy</h3>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Max Budget ($)</label>
              <input
                type="number"
                {...register('buyer_max_budget', {
                  required: 'Required',
                  min: { value: BUYER_CONSTRAINTS.max_budget.min, message: `Min $${BUYER_CONSTRAINTS.max_budget.min}` },
                  max: { value: BUYER_CONSTRAINTS.max_budget.max, message: `Max $${BUYER_CONSTRAINTS.max_budget.max}` },
                })}
                className="w-full border rounded px-3 py-2"
              />
              {errors.buyer_max_budget && <p className="text-red-500 text-sm">{errors.buyer_max_budget.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Max Delivery (days)</label>
              <input
                type="number"
                {...register('buyer_max_delivery_days', {
                  required: 'Required',
                  min: { value: BUYER_CONSTRAINTS.max_delivery_days.min, message: `Min ${BUYER_CONSTRAINTS.max_delivery_days.min}` },
                  max: { value: BUYER_CONSTRAINTS.max_delivery_days.max, message: `Max ${BUYER_CONSTRAINTS.max_delivery_days.max}` },
                })}
                className="w-full border rounded px-3 py-2"
              />
              {errors.buyer_max_delivery_days && <p className="text-red-500 text-sm">{errors.buyer_max_delivery_days.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Min SLA Penalty (%)</label>
              <input
                type="number"
                step="0.1"
                {...register('buyer_min_sla_percent', {
                  required: 'Required',
                  min: { value: BUYER_CONSTRAINTS.min_sla_percent.min, message: `Min ${BUYER_CONSTRAINTS.min_sla_percent.min}%` },
                  max: { value: BUYER_CONSTRAINTS.min_sla_percent.max, message: `Max ${BUYER_CONSTRAINTS.min_sla_percent.max}%` },
                })}
                className="w-full border rounded px-3 py-2"
              />
              {errors.buyer_min_sla_percent && <p className="text-red-500 text-sm">{errors.buyer_min_sla_percent.message}</p>}
            </div>
          </div>
        </div>

        <div className="bg-green-50 p-6 rounded-lg">
          <h3 className="text-lg font-semibold text-green-700 mb-4">Vendor Policy</h3>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Min Price ($)</label>
              <input
                type="number"
                {...register('vendor_min_price', {
                  required: 'Required',
                  min: { value: VENDOR_CONSTRAINTS.min_price.min, message: `Min $${VENDOR_CONSTRAINTS.min_price.min}` },
                })}
                className="w-full border rounded px-3 py-2"
              />
              {errors.vendor_min_price && <p className="text-red-500 text-sm">{errors.vendor_min_price.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Min Delivery (days)</label>
              <input
                type="number"
                {...register('vendor_min_delivery_days', {
                  required: 'Required',
                  min: { value: VENDOR_CONSTRAINTS.min_delivery_days.min, message: `Min ${VENDOR_CONSTRAINTS.min_delivery_days.min}` },
                })}
                className="w-full border rounded px-3 py-2"
              />
              {errors.vendor_min_delivery_days && <p className="text-red-500 text-sm">{errors.vendor_min_delivery_days.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Max SLA Penalty (%)</label>
              <input
                type="number"
                step="0.1"
                {...register('vendor_max_sla_percent', {
                  required: 'Required',
                  min: { value: VENDOR_CONSTRAINTS.max_sla_percent.min, message: `Min ${VENDOR_CONSTRAINTS.max_sla_percent.min}%` },
                  max: { value: VENDOR_CONSTRAINTS.max_sla_percent.max, message: `Max ${VENDOR_CONSTRAINTS.max_sla_percent.max}%` },
                })}
                className="w-full border rounded px-3 py-2"
              />
              {errors.vendor_max_sla_percent && <p className="text-red-500 text-sm">{errors.vendor_max_sla_percent.message}</p>}
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6">
        <label className="block text-sm font-medium mb-1">Max Rounds</label>
        <input
          type="number"
          {...register('max_rounds', { required: 'Required', min: 1, max: 50 })}
          className="w-32 border rounded px-3 py-2"
        />
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="mt-6 bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
      >
        {isLoading ? 'Starting...' : 'Start Negotiation'}
      </button>
    </form>
  );
}
