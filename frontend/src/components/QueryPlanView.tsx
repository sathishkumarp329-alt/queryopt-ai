import { AlertTriangle, CheckCircle, Search, Table2 } from 'lucide-react';
import type { ExplainResult, QueryPlanNode } from '../types';

interface QueryPlanViewProps {
  explainResult: ExplainResult;
  execTimeMs: number;
}

function PlanNode({ node, depth }: { node: QueryPlanNode; depth: number }) {
  const isFullScan = node.is_full_scan;
  const isSEARCH = node.detail.toUpperCase().includes('SEARCH');

  const borderColor = isFullScan
    ? 'border-red-500/40 bg-red-500/5'
    : isSEARCH
    ? 'border-emerald-500/40 bg-emerald-500/5'
    : 'border-gray-700 bg-gray-800';

  const dotColor = isFullScan
    ? 'bg-red-400'
    : isSEARCH
    ? 'bg-emerald-400'
    : 'bg-gray-500';

  return (
    <div className={`ml-${depth > 0 ? 6 : 0}`}>
      <div className={`flex items-start gap-3 border rounded-lg p-3 mb-2 ${borderColor}`}>
        <div className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${dotColor}`} />
        <div className="flex-1 min-w-0">
          <p className="text-sm code-font text-gray-200 break-all">{node.detail}</p>
          <div className="flex flex-wrap gap-2 mt-1.5">
            {node.table && (
              <span className="inline-flex items-center gap-1 text-xs text-blue-400 bg-blue-400/10 px-2 py-0.5 rounded">
                <Table2 className="w-3 h-3" />
                {node.table}
              </span>
            )}
            {node.index_used && (
              <span className="inline-flex items-center gap-1 text-xs text-emerald-400 bg-emerald-400/10 px-2 py-0.5 rounded">
                <Search className="w-3 h-3" />
                {node.index_used}
              </span>
            )}
            {isFullScan && (
              <span className="text-xs text-red-400 bg-red-400/10 px-2 py-0.5 rounded border border-red-400/20 font-semibold">
                FULL SCAN
              </span>
            )}
          </div>
        </div>
        <span className="text-xs text-gray-600 shrink-0">#{node.node_id}</span>
      </div>
    </div>
  );
}

function buildTree(nodes: QueryPlanNode[]): { node: QueryPlanNode; depth: number }[] {
  // Flatten with depth based on parent_id chain
  const idMap = new Map(nodes.map((n) => [n.node_id, n]));
  const getDepth = (n: QueryPlanNode): number => {
    if (n.parent_id === 0 || n.parent_id === n.node_id || !idMap.has(n.parent_id)) return 0;
    return 1 + getDepth(idMap.get(n.parent_id)!);
  };
  return nodes.map((node) => ({ node, depth: getDepth(node) }));
}

export default function QueryPlanView({ explainResult, execTimeMs }: QueryPlanViewProps) {
  const tree = buildTree(explainResult.nodes ?? []);

  return (
    <div className="space-y-4">
      {/* Execution time + full scan warning */}
      <div className="flex items-center gap-3 flex-wrap">
        <div className="flex items-center gap-2 bg-gray-800 border border-gray-700 rounded-lg px-4 py-2">
          <span className="text-xs text-gray-500">Execution Time</span>
          <span className="text-sm font-bold text-emerald-400">{execTimeMs.toFixed(1)} ms</span>
        </div>

        {explainResult.has_full_table_scan && (
          <div className="flex items-center gap-2 bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-2">
            <AlertTriangle className="w-4 h-4 text-red-400 shrink-0" />
            <span className="text-xs text-red-400 font-medium">
              Full Table Scan detected on:{' '}
              <strong>{explainResult.tables_with_full_scan.join(', ')}</strong>
            </span>
          </div>
        )}
      </div>

      {/* Summary */}
      {explainResult.summary && (
        <p className="text-sm text-gray-400 bg-gray-800 border border-gray-700 rounded-lg p-3">
          {explainResult.summary}
        </p>
      )}

      {/* Plan tree */}
      <div>
        <p className="text-xs text-gray-500 uppercase tracking-wider mb-3 font-semibold">
          Query Plan
        </p>
        {tree.length === 0 ? (
          <p className="text-sm text-gray-500 text-center py-6">No query plan data available.</p>
        ) : (
          <div className="space-y-0">
            {tree.map(({ node, depth }) => (
              <PlanNode key={node.node_id} node={node} depth={depth} />
            ))}
          </div>
        )}
      </div>

      {/* Indexes used */}
      {explainResult.indexes_used && explainResult.indexes_used.length > 0 && (
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wider mb-2 font-semibold">
            Indexes Used
          </p>
          <div className="flex flex-wrap gap-2">
            {explainResult.indexes_used.map((idx) => (
              <span
                key={idx}
                className="text-xs code-font text-emerald-400 bg-emerald-400/10 border border-emerald-400/20 px-3 py-1 rounded-full"
              >
                {idx}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Tables scanned */}
      {explainResult.tables_scanned && explainResult.tables_scanned.length > 0 && (
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wider mb-2 font-semibold">
            Tables Scanned
          </p>
          <div className="flex flex-wrap gap-2">
            {explainResult.tables_scanned.map((t) => (
              <span
                key={t}
                className={`text-xs code-font px-3 py-1 rounded-full border ${
                  explainResult.tables_with_full_scan?.includes(t)
                    ? 'text-red-400 bg-red-400/10 border-red-400/20'
                    : 'text-blue-400 bg-blue-400/10 border-blue-400/20'
                }`}
              >
                {t}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="flex items-center gap-4 text-xs text-gray-500">
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-red-400 inline-block" />
          Full Table Scan
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-400 inline-block" />
          Index Search
        </span>
        <span className="flex items-center gap-1.5">
          <CheckCircle className="w-3 h-3" />
          Normal
        </span>
      </div>
    </div>
  );
}
