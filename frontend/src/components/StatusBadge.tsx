interface StatusBadgeProps {
  status: string;
}

const STATUS_CONFIG: Record<string, { bg: string; text: string; label: string }> = {
  IDLE: { bg: 'bg-gray-200', text: 'text-gray-700', label: 'Idle' },
  PENDING: { bg: 'bg-yellow-200', text: 'text-yellow-800', label: 'Pending' },
  IN_PROGRESS: { bg: 'bg-blue-200', text: 'text-blue-800', label: 'In Progress' },
  ACCEPTED: { bg: 'bg-green-200', text: 'text-green-800', label: 'Accepted' },
  DEADLOCK: { bg: 'bg-red-200', text: 'text-red-800', label: 'Deadlock' },
  ENDED: { bg: 'bg-gray-200', text: 'text-gray-700', label: 'Ended' },
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const config = STATUS_CONFIG[status] ?? STATUS_CONFIG.IDLE;

  return (
    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${config.bg} ${config.text}`}>
      {status === 'IN_PROGRESS' && (
        <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse mr-2" />
      )}
      {config.label}
    </span>
  );
}
