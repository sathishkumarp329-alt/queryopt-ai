import type { Finding } from '../types';

interface FindingCardProps {
  finding: Finding;
}

const severityConfig = {
  critical: {
    label: 'CRITICAL',
    badge: 'bg-red-500/10 text-red-500 border border-red-500/30',
    border: 'border-l-red-500',
  },
  high: {
    label: 'HIGH',
    badge: 'bg-orange-400/10 text-orange-400 border border-orange-400/30',
    border: 'border-l-orange-400',
  },
  medium: {
    label: 'MEDIUM',
    badge: 'bg-yellow-400/10 text-yellow-400 border border-yellow-400/30',
    border: 'border-l-yellow-400',
  },
  low: {
    label: 'LOW',
    badge: 'bg-blue-400/10 text-blue-400 border border-blue-400/30',
    border: 'border-l-blue-400',
  },
  info: {
    label: 'INFO',
    badge: 'bg-gray-400/10 text-gray-400 border border-gray-400/30',
    border: 'border-l-gray-400',
  },
};

export default function FindingCard({ finding }: FindingCardProps) {
  const cfg = severityConfig[finding.severity] ?? severityConfig.info;

  return (
    <div
      className={`bg-gray-800 border border-gray-700 border-l-4 ${cfg.border} rounded-lg p-4 space-y-2`}
    >
      {/* Header */}
      <div className="flex items-center gap-2 flex-wrap">
        <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${cfg.badge}`}>
          {cfg.label}
        </span>
        <span className="text-xs text-gray-500 bg-gray-700 px-2 py-0.5 rounded-full">
          {finding.category}
        </span>
        {finding.location && (
          <span className="text-xs text-gray-600 ml-auto code-font">{finding.location}</span>
        )}
      </div>

      {/* Title */}
      <h3 className="text-sm font-semibold text-gray-100">{finding.title}</h3>

      {/* Description */}
      <p className="text-sm text-gray-400 leading-relaxed">{finding.description}</p>

      {/* Evidence */}
      {finding.evidence && (
        <pre className="text-xs code-font bg-gray-900 text-gray-300 rounded p-3 overflow-x-auto whitespace-pre-wrap border border-gray-700">
          {finding.evidence}
        </pre>
      )}
    </div>
  );
}
