import { useState } from 'react';
import { ChevronDown, ChevronRight, Clock, Cpu } from 'lucide-react';
import type { AgentTrajectoryEntry } from '../types';

interface AgentTimelineProps {
  trajectory: AgentTrajectoryEntry[];
}

const agentStyle: Record<string, { color: string; bg: string; border: string }> = {
  'SQL Analysis Agent': {
    color: 'text-blue-400',
    bg: 'bg-blue-400/10',
    border: 'border-blue-400/30',
  },
  'Performance Agent': {
    color: 'text-orange-400',
    bg: 'bg-orange-400/10',
    border: 'border-orange-400/30',
  },
  'Index Agent': {
    color: 'text-purple-400',
    bg: 'bg-purple-400/10',
    border: 'border-purple-400/30',
  },
  'Optimization Agent': {
    color: 'text-emerald-400',
    bg: 'bg-emerald-400/10',
    border: 'border-emerald-400/30',
  },
  'Verification Agent': {
    color: 'text-yellow-400',
    bg: 'bg-yellow-400/10',
    border: 'border-yellow-400/30',
  },
  'Report Agent': {
    color: 'text-pink-400',
    bg: 'bg-pink-400/10',
    border: 'border-pink-400/30',
  },
};

function getStyle(name: string) {
  for (const key of Object.keys(agentStyle)) {
    if (name.toLowerCase().includes(key.toLowerCase().split(' ')[0].toLowerCase())) {
      return agentStyle[key];
    }
  }
  return {
    color: 'text-gray-400',
    bg: 'bg-gray-400/10',
    border: 'border-gray-400/30',
  };
}

function ConfidenceBar({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const color =
    pct >= 80 ? 'bg-emerald-400' : pct >= 60 ? 'bg-yellow-400' : 'bg-red-400';
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-gray-700 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full ${color}`}
          style={{ width: `${pct}%`, transition: 'width 0.5s ease' }}
        />
      </div>
      <span className="text-xs text-gray-500 w-8 text-right">{pct}%</span>
    </div>
  );
}

function TimelineStep({
  entry,
  index,
  isLast,
}: {
  entry: AgentTrajectoryEntry;
  index: number;
  isLast: boolean;
}) {
  const [expanded, setExpanded] = useState(false);
  const style = getStyle(entry.agent_name);
  const initials = entry.agent_name
    .split(' ')
    .slice(0, 2)
    .map((w) => w[0])
    .join('');

  return (
    <div className="flex gap-4">
      {/* Timeline spine */}
      <div className="flex flex-col items-center">
        <div
          className={`w-9 h-9 rounded-full flex items-center justify-center text-xs font-bold border ${style.bg} ${style.border} ${style.color} shrink-0 z-10`}
        >
          {initials}
        </div>
        {!isLast && <div className="w-px flex-1 bg-gray-700 mt-1" />}
      </div>

      {/* Content */}
      <div className={`mb-6 flex-1 ${isLast ? '' : ''}`}>
        <div className="bg-gray-800 border border-gray-700 rounded-lg overflow-hidden">
          {/* Header */}
          <button
            onClick={() => setExpanded((e) => !e)}
            className="w-full flex items-start gap-3 p-4 text-left hover:bg-gray-750 transition-colors"
          >
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap mb-1">
                <span className={`text-xs font-bold ${style.color}`}>{entry.agent_name}</span>
                <span className="text-xs text-gray-500 bg-gray-700 px-2 py-0.5 rounded-full">
                  #{index + 1}
                </span>
                {entry.duration_ms > 0 && (
                  <span className="text-xs text-gray-500 flex items-center gap-1 ml-auto">
                    <Clock className="w-3 h-3" />
                    {entry.duration_ms}ms
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-200 font-medium">{entry.action}</p>
              <p className="text-xs text-gray-400 mt-1 line-clamp-2">{entry.result_summary}</p>
            </div>
            <div className="shrink-0 mt-1">
              {expanded ? (
                <ChevronDown className="w-4 h-4 text-gray-500" />
              ) : (
                <ChevronRight className="w-4 h-4 text-gray-500" />
              )}
            </div>
          </button>

          {/* Expanded details */}
          {expanded && (
            <div className="border-t border-gray-700 p-4 space-y-3 bg-gray-900/50">
              {entry.tool_used && (
                <div className="flex items-center gap-2">
                  <Cpu className="w-3.5 h-3.5 text-gray-500" />
                  <span className="text-xs text-gray-500">Tool:</span>
                  <code className="text-xs text-blue-400 bg-blue-400/10 px-2 py-0.5 rounded code-font">
                    {entry.tool_used}
                  </code>
                </div>
              )}

              <div>
                <p className="text-xs text-gray-500 mb-1 uppercase tracking-wider">Input</p>
                <p className="text-xs text-gray-400 bg-gray-800 rounded p-2 border border-gray-700">
                  {entry.input_summary}
                </p>
              </div>

              {entry.finding && (
                <div>
                  <p className="text-xs text-gray-500 mb-1 uppercase tracking-wider">Finding</p>
                  <p className="text-xs text-yellow-400 bg-yellow-400/5 rounded p-2 border border-yellow-400/20">
                    {entry.finding}
                  </p>
                </div>
              )}

              <div>
                <p className="text-xs text-gray-500 mb-1 uppercase tracking-wider">Confidence</p>
                <ConfidenceBar value={entry.confidence} />
              </div>

              <div className="text-xs text-gray-600 flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {new Date(entry.timestamp).toLocaleTimeString()}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function AgentTimeline({ trajectory }: AgentTimelineProps) {
  if (!trajectory || trajectory.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <Cpu className="w-10 h-10 mx-auto mb-3 opacity-40" />
        <p className="text-sm">No agent trajectory data available.</p>
      </div>
    );
  }

  return (
    <div className="space-y-0">
      <div className="flex items-center gap-2 mb-6">
        <Cpu className="w-4 h-4 text-emerald-400" />
        <h3 className="text-sm font-semibold text-gray-300">
          Agent Execution — {trajectory.length} steps
        </h3>
      </div>
      {trajectory.map((entry, i) => (
        <TimelineStep
          key={i}
          entry={entry}
          index={i}
          isLast={i === trajectory.length - 1}
        />
      ))}
    </div>
  );
}
