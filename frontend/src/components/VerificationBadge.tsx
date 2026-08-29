import { CheckCircle, XCircle, AlertTriangle, TrendingDown, TrendingUp } from 'lucide-react';
import type { VerificationResult } from '../types';

interface VerificationBadgeProps {
  verification: VerificationResult;
}

function CheckRow({
  label,
  value,
}: {
  label: string;
  value: boolean;
}) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-gray-700 last:border-0">
      <span className="text-sm text-gray-400">{label}</span>
      {value ? (
        <span className="flex items-center gap-1.5 text-emerald-400 text-sm font-medium">
          <CheckCircle className="w-4 h-4" />
          Passed
        </span>
      ) : (
        <span className="flex items-center gap-1.5 text-red-400 text-sm font-medium">
          <XCircle className="w-4 h-4" />
          Failed
        </span>
      )}
    </div>
  );
}

const statusConfig = {
  VERIFIED: {
    label: 'VERIFIED',
    icon: CheckCircle,
    className: 'text-emerald-400 bg-emerald-400/10 border-emerald-400/30',
  },
  UNCERTAIN: {
    label: 'UNCERTAIN',
    icon: AlertTriangle,
    className: 'text-yellow-400 bg-yellow-400/10 border-yellow-400/30',
  },
  FAILED: {
    label: 'FAILED',
    icon: XCircle,
    className: 'text-red-400 bg-red-400/10 border-red-400/30',
  },
};

export default function VerificationBadge({ verification }: VerificationBadgeProps) {
  const cfg = statusConfig[verification.status] ?? statusConfig.UNCERTAIN;
  const Icon = cfg.icon;

  const improvement = verification.improvement_pct;
  const improved = improvement > 0;
  const noChange = improvement === 0;

  const confidencePct = Math.round(verification.confidence * 100);
  const confColor =
    confidencePct >= 80
      ? 'bg-emerald-400'
      : confidencePct >= 60
      ? 'bg-yellow-400'
      : 'bg-red-400';

  return (
    <div className="space-y-4">
      {/* Status badge */}
      <div
        className={`flex items-center gap-3 px-4 py-3 rounded-lg border ${cfg.className}`}
      >
        <Icon className="w-5 h-5 shrink-0" />
        <div>
          <p className="font-bold text-sm">{cfg.label}</p>
          <p className="text-xs opacity-80">Optimization verification result</p>
        </div>
      </div>

      {/* Checks */}
      <div className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2">
        <CheckRow label="Syntax Valid" value={verification.syntax_valid} />
        <CheckRow label="Tables Valid" value={verification.tables_valid} />
        <CheckRow label="Results Equivalent" value={verification.is_equivalent} />
      </div>

      {/* Performance comparison */}
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-3">
          Performance Comparison
        </p>
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <p className="text-xs text-gray-500 mb-1">Original</p>
            <p className="text-lg font-bold text-gray-100">
              {verification.original_time_ms.toFixed(1)}
              <span className="text-xs text-gray-500 ml-1">ms</span>
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500 mb-1">Optimized</p>
            <p className="text-lg font-bold text-gray-100">
              {verification.optimized_time_ms.toFixed(1)}
              <span className="text-xs text-gray-500 ml-1">ms</span>
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500 mb-1">Improvement</p>
            <p
              className={`text-lg font-bold flex items-center justify-center gap-1 ${
                noChange
                  ? 'text-gray-400'
                  : improved
                  ? 'text-emerald-400'
                  : 'text-red-400'
              }`}
            >
              {improved ? (
                <TrendingUp className="w-4 h-4" />
              ) : !noChange ? (
                <TrendingDown className="w-4 h-4" />
              ) : null}
              {improvement > 0 ? '+' : ''}
              {improvement.toFixed(1)}%
            </p>
          </div>
        </div>
      </div>

      {/* Confidence bar */}
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <div className="flex items-center justify-between mb-2">
          <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">
            Confidence
          </p>
          <span className="text-sm font-bold text-gray-200">{confidencePct}%</span>
        </div>
        <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full ${confColor}`}
            style={{ width: `${confidencePct}%`, transition: 'width 0.5s ease' }}
          />
        </div>
      </div>

      {/* Equivalence explanation */}
      {verification.equivalence_explanation && (
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
          <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-2">
            Equivalence Analysis
          </p>
          <p className="text-sm text-gray-300 leading-relaxed">
            {verification.equivalence_explanation}
          </p>
        </div>
      )}
    </div>
  );
}
