import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { Play, RotateCcw, CheckCircle2, AlertTriangle, Database, Sparkles, Layers } from 'lucide-react';
import SqlEditor from '../components/SqlEditor';
import { analyzeQuery, analyzeBaseline, validateQuery } from '../services/api';

const PRESET_QUERIES = [
  {
    name: '1. Non-Sargable YEAR() Function Filter (High Optimization Potential)',
    sql: "SELECT * FROM orders WHERE strftime('%Y', order_date) = '2024';"
  },
  {
    name: '2. Unnecessary SELECT * on Wide Table',
    sql: "SELECT * FROM customers;"
  },
  {
    name: '3. Missing WHERE Clause on Large Orders Table',
    sql: "SELECT order_id, total_amount, shipping_city FROM orders;"
  },
  {
    name: '4. Filter on Unindexed Column (Full Scan)',
    sql: "SELECT order_id, total_amount FROM orders WHERE shipping_city = 'Chicago';"
  },
  {
    name: '5. Leading Wildcard in LIKE Condition',
    sql: "SELECT customer_id, first_name, email FROM customers WHERE email LIKE '%@example.com';"
  },
  {
    name: '6. Redundant DISTINCT with GROUP BY',
    sql: "SELECT DISTINCT status, COUNT(*) as count FROM orders GROUP BY status;"
  },
  {
    name: '7. Cartesian Product Missing Join Condition',
    sql: "SELECT customers.first_name, orders.order_id FROM customers, orders;"
  },
  {
    name: '8. Composite Index Opportunity (Filter + Sort)',
    sql: "SELECT order_id, customer_id, total_amount FROM orders WHERE status = 'delivered' ORDER BY order_date DESC LIMIT 50;"
  },
  {
    name: '9. Multi-Table Join with SELECT *',
    sql: "SELECT * FROM orders o JOIN order_items oi ON o.order_id = oi.order_id JOIN products p ON oi.product_id = p.product_id WHERE o.order_id = 100;"
  },
  {
    name: '10. Already Optimal Filtered Query',
    sql: "SELECT o.order_id, o.order_date, c.first_name FROM orders o JOIN customers c ON o.customer_id = c.customer_id WHERE o.customer_id = 42;"
  }
];

export default function Analyzer() {
  const navigate = useNavigate();
  const [sql, setSql] = useState(PRESET_QUERIES[0].sql);
  const [dbType, setDbType] = useState('sqlite');
  const [schema, setSchema] = useState('demo');
  const [loading, setLoading] = useState(false);
  const [activeStep, setActiveStep] = useState<string | null>(null);
  const [validation, setValidation] = useState<{ valid: boolean; error: string | null; isDestructive: boolean } | null>(null);

  const handleValidate = async () => {
    try {
      const res = await validateQuery(sql);
      setValidation({
        valid: res.valid,
        error: res.error,
        isDestructive: res.is_destructive
      });
    } catch (err: any) {
      setValidation({
        valid: false,
        error: err.response?.data?.detail || err.message,
        isDestructive: false
      });
    }
  };

  const handleAnalyzeAgentic = async () => {
    setLoading(true);
    setActiveStep('Parsing SQL AST & Antipatterns...');
    try {
      setTimeout(() => setActiveStep('Analyzing Physical EXPLAIN & Query Execution...'), 300);
      setTimeout(() => setActiveStep('Evaluating Index Coverage & Recommendations...'), 600);
      setTimeout(() => setActiveStep('Generating Optimized Rewrite & Benchmark Verification...'), 900);

      const res = await analyzeQuery(sql, dbType, schema);
      navigate(`/results/${res.analysis_id}`);
    } catch (err: any) {
      alert(`Analysis failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
      setActiveStep(null);
    }
  };

  const handleAnalyzeBaseline = async () => {
    setLoading(true);
    setActiveStep('Running Traditional Rule Engine...');
    try {
      const res: any = await analyzeBaseline(sql, schema);
      navigate(`/results/${res.analysis_id}`);
    } catch (err: any) {
      alert(`Baseline analysis failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
      setActiveStep(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-100 flex items-center gap-2">
          <Sparkles className="w-7 h-7 text-emerald-400" />
          SQL Query Analyzer
        </h1>
        <p className="text-gray-400 mt-1">
          Input any SQL query to trigger the 6-agent analysis, performance benchmarking, index recommendation, and verification workflow.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: SQL Editor (2 cols) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 space-y-4">
            {/* Presets & Controls */}
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex-1 min-w-[280px]">
                <label className="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-1">
                  Preset Benchmark Queries
                </label>
                <select
                  className="w-full bg-gray-950 border border-gray-800 rounded-lg px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-emerald-500"
                  onChange={(e) => {
                    const found = PRESET_QUERIES.find((q) => q.name === e.target.value);
                    if (found) {
                      setSql(found.sql);
                      setValidation(null);
                    }
                  }}
                >
                  {PRESET_QUERIES.map((q) => (
                    <option key={q.name} value={q.name}>
                      {q.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex items-end">
                <button
                  onClick={() => {
                    setSql('');
                    setValidation(null);
                  }}
                  className="px-3 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg text-sm flex items-center gap-1.5 transition"
                >
                  <RotateCcw className="w-4 h-4" />
                  Clear
                </button>
              </div>
            </div>

            {/* Editor */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">
                SQL Editor (SQLite / MySQL Dialect)
              </label>
              <SqlEditor value={sql} onChange={(val) => setSql(val)} height="280px" />
            </div>

            {/* Validation Banner */}
            {validation && (
              <div
                className={`p-3 rounded-lg border text-sm flex items-start gap-2 ${
                  validation.valid
                    ? 'bg-emerald-950/40 border-emerald-800/50 text-emerald-300'
                    : 'bg-red-950/40 border-red-800/50 text-red-300'
                }`}
              >
                {validation.valid ? (
                  <CheckCircle2 className="w-5 h-5 flex-shrink-0 text-emerald-400 mt-0.5" />
                ) : (
                  <AlertTriangle className="w-5 h-5 flex-shrink-0 text-red-400 mt-0.5" />
                )}
                <div>
                  <div className="font-semibold">
                    {validation.valid ? 'Query Valid & Safe' : 'Validation Failed / Security Block'}
                  </div>
                  {validation.error && <div className="text-xs mt-1 text-gray-300">{validation.error}</div>}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Execution Configuration & Actions (1 col) */}
        <div className="space-y-4">
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 space-y-4">
            <h2 className="text-base font-semibold text-gray-200 flex items-center gap-2">
              <Database className="w-5 h-5 text-blue-400" />
              Target Database
            </h2>

            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1">Engine Dialect</label>
              <select
                value={dbType}
                onChange={(e) => setDbType(e.target.value)}
                className="w-full bg-gray-950 border border-gray-800 rounded-lg px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-emerald-500"
              >
                <option value="sqlite">SQLite (Embedded Demo DB)</option>
                <option value="mysql">MySQL 8.0 (Compatible Mode)</option>
                <option value="postgresql">PostgreSQL (Compatible Mode)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1">Schema Environment</label>
              <select
                value={schema}
                onChange={(e) => setSchema(e.target.value)}
                className="w-full bg-gray-950 border border-gray-800 rounded-lg px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-emerald-500"
              >
                <option value="demo">Demo E-Commerce Database (8,000+ records)</option>
              </select>
            </div>

            <div className="pt-2 border-t border-gray-800 space-y-3">
              <button
                onClick={handleAnalyzeAgentic}
                disabled={loading || !sql.trim()}
                className="w-full bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-semibold py-3 px-4 rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-emerald-950 transition"
              >
                <Sparkles className="w-5 h-5" />
                {loading ? 'Executing Agent Pipeline...' : 'Analyze with QueryOpt AI'}
              </button>

              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={handleAnalyzeBaseline}
                  disabled={loading || !sql.trim()}
                  className="bg-gray-800 hover:bg-gray-700 disabled:opacity-50 text-gray-300 text-xs font-medium py-2.5 px-3 rounded-lg flex items-center justify-center gap-1.5 transition"
                >
                  <Layers className="w-4 h-4" />
                  Baseline Rules
                </button>

                <button
                  onClick={handleValidate}
                  disabled={loading || !sql.trim()}
                  className="bg-gray-800 hover:bg-gray-700 disabled:opacity-50 text-gray-300 text-xs font-medium py-2.5 px-3 rounded-lg flex items-center justify-center gap-1.5 transition"
                >
                  <Play className="w-4 h-4" />
                  Validate Only
                </button>
              </div>
            </div>
          </div>

          {/* Active Step Indicator when analyzing */}
          {loading && (
            <div className="bg-gray-900 border border-emerald-800/40 rounded-xl p-4 text-center space-y-3 animate-pulse">
              <div className="w-6 h-6 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin mx-auto" />
              <div className="text-sm font-medium text-emerald-400">{activeStep}</div>
              <div className="text-xs text-gray-400">
                SQL Agent &bull; Performance Agent &bull; Index Agent &bull; Optimization Agent &bull; Verification Agent
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
