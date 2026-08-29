import { useState } from 'react';
import { CheckCircle, Copy, Check, Database, Zap } from 'lucide-react';
import type { IndexRecommendation } from '../types';

interface IndexRecommendationCardProps {
  recommendations: IndexRecommendation[];
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  const copy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  return (
    <button
      onClick={copy}
      className="flex items-center gap-1.5 text-xs text-gray-400 hover:text-gray-100 transition-colors px-2 py-1 rounded bg-gray-700 hover:bg-gray-600"
    >
      {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
      {copied ? 'Copied' : 'Copy'}
    </button>
  );
}

const impactColors: Record<string, string> = {
  HIGH: 'text-emerald-400 bg-emerald-400/10 border-emerald-400/30',
  MEDIUM: 'text-yellow-400 bg-yellow-400/10 border-yellow-400/30',
  LOW: 'text-blue-400 bg-blue-400/10 border-blue-400/30',
};

function getImpactClass(impact: string) {
  const key = impact.toUpperCase();
  for (const k of Object.keys(impactColors)) {
    if (key.includes(k)) return impactColors[k];
  }
  return 'text-gray-400 bg-gray-400/10 border-gray-400/30';
}

export default function IndexRecommendationCard({
  recommendations,
}: IndexRecommendationCardProps) {
  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="bg-gray-800 border border-gray-700 rounded-xl p-8 text-center">
        <CheckCircle className="w-10 h-10 text-emerald-400 mx-auto mb-3" />
        <p className="text-gray-300 font-medium">No Index Recommendations</p>
        <p className="text-sm text-gray-500 mt-1">
          Existing indexes appear sufficient for this query.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-2">
        <Database className="w-4 h-4 text-purple-400" />
        <h3 className="text-sm font-semibold text-gray-300">
          {recommendations.length} Index Recommendation{recommendations.length !== 1 ? 's' : ''}
        </h3>
      </div>

      {recommendations.map((rec, i) => (
        <div
          key={i}
          className="bg-gray-800 border border-gray-700 rounded-lg overflow-hidden"
        >
          {/* Header */}
          <div className="flex items-center gap-3 px-4 py-3 border-b border-gray-700 bg-gray-800/80">
            <Database className="w-4 h-4 text-purple-400 shrink-0" />
            <div className="flex-1 min-w-0">
              <span className="text-sm font-semibold text-gray-100">{rec.table_name}</span>
              <span className="text-xs text-gray-500 ml-2">({rec.index_type})</span>
            </div>
            <span
              className={`text-xs font-bold px-2 py-0.5 rounded-full border ${getImpactClass(
                rec.expected_impact,
              )}`}
            >
              {rec.expected_impact} Impact
            </span>
          </div>

          {/* Body */}
          <div className="p-4 space-y-3">
            {/* Columns */}
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs text-gray-500">Columns:</span>
              {rec.columns.map((col) => (
                <code
                  key={col}
                  className="text-xs code-font text-blue-400 bg-blue-400/10 px-2 py-0.5 rounded"
                >
                  {col}
                </code>
              ))}
            </div>

            {/* Reason */}
            <p className="text-sm text-gray-400">{rec.reason}</p>

            {/* CREATE INDEX statement */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5 text-xs text-gray-500">
                  <Zap className="w-3 h-3" />
                  CREATE INDEX Statement
                </div>
                <CopyButton text={rec.create_statement} />
              </div>
              <pre className="text-xs code-font bg-gray-900 text-emerald-300 rounded p-3 overflow-x-auto border border-gray-700 whitespace-pre-wrap">
                {rec.create_statement}
              </pre>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
