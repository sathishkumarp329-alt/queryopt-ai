import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import {
  BarChart3,
  Database,
  AlertTriangle,
  TrendingUp,
  Clock,
  ChevronRight,
} from 'lucide-react';
import { getHistory } from '../services/api';
import type { HistoryItem } from '../types';

function StatCard({
  icon: Icon,
  label,
  value,
  sub,
  color,
}: {
  icon: React.ElementType;
  label: string;
  value: string | number;
  sub?: string;
  color?: string;
}) {
  return (
    <div className="bg-gray-800 border border-gray-700 rounded-xl p-5 flex items-start gap-4">
      <div
        className={`w-10 h-10 rounded-lg flex items-center justify-center ${
          color ?? 'bg-emerald-500/20'
        }`}
      >
        <Icon
          className={`w-5 h-5 ${
            color?.includes('orange')
              ? 'text-orange-400'
              : color?.includes('red')
              ? 'text-red-400'
              : color?.includes('blue')
              ? 'text-blue-400'
              : 'text-emerald-400'
          }`}
        />
      </div>
      <div>
        <p className="text-2xl font-bold text-gray-100">{value}</p>
        <p className="text-sm text-gray-400">{label}</p>
        {sub && <p className="text-xs text-gray-600 mt-0.5">{sub}</p>}
      </div>
    </div>
  );
}

const potentialColors: Record<string, string> = {
  HIGH: 'text-red-400 bg-red-400/10',
  MEDIUM: 'text-yellow-400 bg-yellow-400/10',
  LOW: 'text-blue-400 bg-blue-400/10',
  NONE: 'text-gray-400 bg-gray-700',
};

export default function Dashboard() {
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    (async () => {
      try {
        const res = await getHistory(1, 50);
        setItems(res.items);
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : 'Failed to load history');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const totalQueries = items.length;
  const avgSqlScore =
    items.length > 0
      ? Math.round(
          items.reduce((s, i) => s + (i.sql_score ?? 0), 0) / items.filter((i) => i.sql_score != null).length || 0,
        )
      : 0;

  // We don't have per-item finding counts in history; use optimization_potential as proxy
  const highPotential = items.filter(
    (i) => i.optimization_potential === 'HIGH',
  ).length;

  const avgImprovementPct =
    items.filter((i) => i.performance_score != null).length > 0
      ? Math.round(
          items.reduce((s, i) => s + (i.performance_score ?? 0), 0) /
            items.filter((i) => i.performance_score != null).length,
        )
      : 0;

  // Chart data: last 20 analyses sorted by time
  const chartData = [...items]
    .sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
    .slice(-20)
    .map((i) => ({
      date: new Date(i.created_at).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
      }),
      sqlScore: i.sql_score ?? 0,
      perfScore: i.performance_score ?? 0,
    }));

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-100">Dashboard</h1>
        <p className="text-sm text-gray-400 mt-1">
          SQL analysis overview and recent activity
        </p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-24">
          <div className="w-8 h-8 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : error ? (
        <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-6 text-red-400 text-sm">
          {error} — Make sure the backend is running on port 8000.
        </div>
      ) : (
        <>
          {/* Stats */}
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
            <StatCard
              icon={Database}
              label="Total Queries Analyzed"
              value={totalQueries}
              sub="All time"
            />
            <StatCard
              icon={BarChart3}
              label="Avg SQL Score"
              value={`${avgSqlScore}/100`}
              color="bg-blue-500/20"
            />
            <StatCard
              icon={AlertTriangle}
              label="High Potential Issues"
              value={highPotential}
              sub="Queries needing attention"
              color="bg-orange-500/20"
            />
            <StatCard
              icon={TrendingUp}
              label="Avg Performance Score"
              value={`${avgImprovementPct}/100`}
              color="bg-red-500/20"
            />
          </div>

          {/* Chart */}
          {chartData.length > 0 && (
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-5">
              <h2 className="text-sm font-semibold text-gray-300 mb-4">
                SQL Score Trend — Last {chartData.length} Analyses
              </h2>
              <ResponsiveContainer width="100%" height={220}>
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="sqlGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#34d399" stopOpacity={0.25} />
                      <stop offset="95%" stopColor="#34d399" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="perfGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#60a5fa" stopOpacity={0.2} />
                      <stop offset="95%" stopColor="#60a5fa" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(55,65,81,0.5)" />
                  <XAxis
                    dataKey="date"
                    tick={{ fill: '#6b7280', fontSize: 11 }}
                    axisLine={{ stroke: '#374151' }}
                    tickLine={false}
                  />
                  <YAxis
                    domain={[0, 100]}
                    tick={{ fill: '#6b7280', fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1f2937',
                      border: '1px solid #374151',
                      borderRadius: '8px',
                      color: '#f3f4f6',
                      fontSize: '12px',
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="sqlScore"
                    name="SQL Score"
                    stroke="#34d399"
                    strokeWidth={2}
                    fill="url(#sqlGrad)"
                    dot={{ fill: '#34d399', r: 3, strokeWidth: 0 }}
                    activeDot={{ r: 5, fill: '#34d399' }}
                  />
                  <Area
                    type="monotone"
                    dataKey="perfScore"
                    name="Perf Score"
                    stroke="#60a5fa"
                    strokeWidth={2}
                    fill="url(#perfGrad)"
                    dot={{ fill: '#60a5fa', r: 3, strokeWidth: 0 }}
                    activeDot={{ r: 5, fill: '#60a5fa' }}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Recent Analyses */}
          <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden">
            <div className="px-5 py-4 border-b border-gray-700 flex items-center justify-between">
              <h2 className="text-sm font-semibold text-gray-300">Recent Analyses</h2>
              <button
                onClick={() => navigate('/history')}
                className="text-xs text-emerald-400 hover:text-emerald-300 flex items-center gap-1"
              >
                View all <ChevronRight className="w-3 h-3" />
              </button>
            </div>

            {items.length === 0 ? (
              <div className="text-center py-16 text-gray-500">
                <Database className="w-10 h-10 mx-auto mb-3 opacity-30" />
                <p className="text-sm">No queries analyzed yet.</p>
                <button
                  onClick={() => navigate('/analyzer')}
                  className="mt-3 text-sm text-emerald-400 hover:underline"
                >
                  Analyze your first query →
                </button>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-xs text-gray-500 uppercase tracking-wider border-b border-gray-700">
                      <th className="px-5 py-3 text-left">Time</th>
                      <th className="px-5 py-3 text-left">SQL Snippet</th>
                      <th className="px-5 py-3 text-left">Score</th>
                      <th className="px-5 py-3 text-left">Potential</th>
                      <th className="px-5 py-3 text-left">Status</th>
                      <th className="px-5 py-3" />
                    </tr>
                  </thead>
                  <tbody>
                    {items.slice(0, 10).map((item) => (
                      <tr
                        key={item.id}
                        onClick={() => navigate(`/results/${item.id}`)}
                        className="border-b border-gray-700/50 hover:bg-gray-700/30 cursor-pointer transition-colors"
                      >
                        <td className="px-5 py-3 text-gray-400 whitespace-nowrap">
                          <span className="flex items-center gap-1.5">
                            <Clock className="w-3 h-3" />
                            {new Date(item.created_at).toLocaleString('en-US', {
                              month: 'short',
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit',
                            })}
                          </span>
                        </td>
                        <td className="px-5 py-3">
                          <code className="text-xs code-font text-gray-300 truncate block max-w-xs">
                            {item.original_sql.slice(0, 60)}
                            {item.original_sql.length > 60 ? '…' : ''}
                          </code>
                        </td>
                        <td className="px-5 py-3">
                          <span
                            className={`font-bold ${
                              (item.sql_score ?? 0) >= 80
                                ? 'text-emerald-400'
                                : (item.sql_score ?? 0) >= 60
                                ? 'text-yellow-400'
                                : 'text-red-400'
                            }`}
                          >
                            {item.sql_score ?? '—'}
                          </span>
                        </td>
                        <td className="px-5 py-3">
                          {item.optimization_potential ? (
                            <span
                              className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
                                potentialColors[item.optimization_potential] ?? 'text-gray-400'
                              }`}
                            >
                              {item.optimization_potential}
                            </span>
                          ) : (
                            <span className="text-gray-600">—</span>
                          )}
                        </td>
                        <td className="px-5 py-3">
                          <span
                            className={`text-xs px-2 py-0.5 rounded-full ${
                              item.status === 'completed'
                                ? 'text-emerald-400 bg-emerald-400/10'
                                : item.status === 'failed'
                                ? 'text-red-400 bg-red-400/10'
                                : 'text-yellow-400 bg-yellow-400/10'
                            }`}
                          >
                            {item.status}
                          </span>
                        </td>
                        <td className="px-5 py-3 text-right">
                          <ChevronRight className="w-4 h-4 text-gray-600 ml-auto" />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
