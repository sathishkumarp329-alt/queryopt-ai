import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Clock, Search, Trash2, ArrowRight, Database, Sparkles } from 'lucide-react';
import { getHistory, deleteAnalysis } from '../services/api';
import { HistoryItem } from '../types';

export default function History() {
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchItems = (p: number) => {
    setLoading(true);
    getHistory(p, 20)
      .then((res) => {
        setItems(res.items);
        setTotal(res.total);
      })
      .catch((err) => console.error('Error fetching history:', err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchItems(page);
  }, [page]);

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    e.preventDefault();
    if (confirm('Delete this analysis record?')) {
      try {
        await deleteAnalysis(id);
        fetchItems(page);
      } catch (err: any) {
        alert(`Delete failed: ${err.message}`);
      }
    }
  };

  const filteredItems = items.filter((item) =>
    item.original_sql.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-100 flex items-center gap-2">
            <Clock className="w-7 h-7 text-emerald-400" />
            Query Analysis History
          </h1>
          <p className="text-gray-400 mt-1">
            Browse, review, and compare previously analyzed SQL queries and their optimization scores.
          </p>
        </div>

        {/* Search Input */}
        <div className="relative min-w-[280px]">
          <Search className="w-4 h-4 absolute left-3 top-3 text-gray-500" />
          <input
            type="text"
            placeholder="Search SQL query text..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-gray-900 border border-gray-800 rounded-lg pl-9 pr-4 py-2 text-sm text-gray-200 focus:outline-none focus:border-emerald-500"
          />
        </div>
      </div>

      {/* History Table */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-gray-400">Loading history...</div>
        ) : filteredItems.length === 0 ? (
          <div className="p-12 text-center space-y-4">
            <Database className="w-12 h-12 text-gray-600 mx-auto" />
            <h3 className="text-lg font-semibold text-gray-300">No Query Analyses Yet</h3>
            <p className="text-sm text-gray-500">Run your first query analysis to populate this history log.</p>
            <Link
              to="/analyzer"
              className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-sm font-medium transition"
            >
              <Sparkles className="w-4 h-4" /> Go to SQL Analyzer
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-gray-300">
              <thead className="bg-gray-950 text-gray-400 uppercase text-xs">
                <tr>
                  <th className="py-3 px-4">Date / Time</th>
                  <th className="py-3 px-4">Target SQL Query</th>
                  <th className="py-3 px-4">SQL Score</th>
                  <th className="py-3 px-4">Perf Score</th>
                  <th className="py-3 px-4">Potential</th>
                  <th className="py-3 px-4">Duration</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {filteredItems.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-800/50 transition">
                    <td className="py-3.5 px-4 text-xs text-gray-400 whitespace-nowrap">
                      {new Date(item.created_at).toLocaleString()}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-xs text-gray-200 max-w-md truncate">
                      {item.original_sql}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className={`font-semibold ${
                        (item.sql_score || 0) >= 80
                          ? 'text-emerald-400'
                          : (item.sql_score || 0) >= 60
                          ? 'text-yellow-400'
                          : 'text-red-400'
                      }`}>
                        {item.sql_score !== null ? `${item.sql_score}/100` : '—'}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className={`font-semibold ${
                        (item.performance_score || 0) >= 80
                          ? 'text-emerald-400'
                          : 'text-yellow-400'
                      }`}>
                        {item.performance_score !== null ? `${item.performance_score}/100` : '—'}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className={`px-2 py-0.5 rounded text-xs font-semibold ${
                        item.optimization_potential === 'HIGH'
                          ? 'bg-red-500/20 text-red-400'
                          : item.optimization_potential === 'MEDIUM'
                          ? 'bg-yellow-500/20 text-yellow-400'
                          : 'bg-blue-500/20 text-blue-400'
                      }`}>
                        {item.optimization_potential || 'NONE'}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-xs text-gray-400">
                      {item.duration_seconds ? `${item.duration_seconds}s` : '—'}
                    </td>
                    <td className="py-3.5 px-4 text-right whitespace-nowrap">
                      <div className="flex items-center justify-end gap-2">
                        <Link
                          to={`/results/${item.id}`}
                          className="px-3 py-1.5 bg-emerald-950/40 hover:bg-emerald-900/60 text-emerald-400 rounded-lg text-xs font-medium flex items-center gap-1 transition"
                        >
                          View <ArrowRight className="w-3 h-3" />
                        </Link>
                        <button
                          onClick={(e) => handleDelete(item.id, e)}
                          className="p-1.5 text-gray-500 hover:text-red-400 rounded-lg transition"
                          title="Delete Record"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {total > 20 && (
          <div className="p-4 border-t border-gray-800 flex items-center justify-between text-xs text-gray-400">
            <div>
              Showing {Math.min((page - 1) * 20 + 1, total)} - {Math.min(page * 20, total)} of {total} records
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-3 py-1 bg-gray-800 disabled:opacity-40 rounded"
              >
                Previous
              </button>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={page * 20 >= total}
                className="px-3 py-1 bg-gray-800 disabled:opacity-40 rounded"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
