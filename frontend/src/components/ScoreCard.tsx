interface ScoreCardProps {
  sqlScore: number;
  performanceScore: number;
  potential: string;
}

function CircleScore({ score, label }: { score: number; label: string }) {
  const r = 40;
  const circ = 2 * Math.PI * r;
  const pct = Math.max(0, Math.min(100, score));
  const dash = (pct / 100) * circ;

  const color =
    pct >= 80
      ? { stroke: '#34d399', text: 'text-emerald-400' }
      : pct >= 60
      ? { stroke: '#facc15', text: 'text-yellow-400' }
      : { stroke: '#f87171', text: 'text-red-400' };

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative w-28 h-28">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
          {/* Background track */}
          <circle
            cx="50"
            cy="50"
            r={r}
            fill="none"
            stroke="rgb(31 41 55)"
            strokeWidth="8"
          />
          {/* Progress */}
          <circle
            cx="50"
            cy="50"
            r={r}
            fill="none"
            stroke={color.stroke}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={`${dash} ${circ - dash}`}
            strokeDashoffset={0}
            style={{ transition: 'stroke-dasharray 0.6s ease' }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`text-2xl font-bold ${color.text}`}>{pct}</span>
          <span className="text-xs text-gray-500">/100</span>
        </div>
      </div>
      <p className="text-sm text-gray-400 font-medium">{label}</p>
    </div>
  );
}

const potentialConfig: Record<
  string,
  { label: string; className: string }
> = {
  HIGH: {
    label: 'HIGH Optimization Potential',
    className: 'bg-red-500/10 text-red-400 border border-red-500/30',
  },
  MEDIUM: {
    label: 'MEDIUM Optimization Potential',
    className: 'bg-yellow-400/10 text-yellow-400 border border-yellow-400/30',
  },
  LOW: {
    label: 'LOW Optimization Potential',
    className: 'bg-blue-400/10 text-blue-400 border border-blue-400/30',
  },
  NONE: {
    label: 'No Optimization Needed',
    className: 'bg-gray-400/10 text-gray-400 border border-gray-400/30',
  },
};

export default function ScoreCard({ sqlScore, performanceScore, potential }: ScoreCardProps) {
  const pot = potentialConfig[potential] ?? potentialConfig['NONE'];

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
      <div className="flex flex-col sm:flex-row items-center justify-around gap-6">
        <CircleScore score={sqlScore} label="SQL Quality" />
        <CircleScore score={performanceScore} label="Performance" />
        <div className="flex flex-col items-center gap-3">
          <p className="text-sm text-gray-500 uppercase tracking-wider font-semibold">
            Optimization
          </p>
          <span
            className={`px-4 py-2 rounded-full text-sm font-bold tracking-wide ${pot.className}`}
          >
            {pot.label}
          </span>
        </div>
      </div>
    </div>
  );
}
