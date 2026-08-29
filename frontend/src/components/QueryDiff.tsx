import { useState } from 'react';
import { Copy, Check, ArrowLeftRight } from 'lucide-react';
import SqlEditor from './SqlEditor';

interface QueryDiffProps {
  original: string;
  optimized: string;
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

/** Compute line-level diff: returns arrays of {line, type: 'added'|'removed'|'same'} */
function computeDiff(original: string, optimized: string) {
  const origLines = original.split('\n');
  const optLines = optimized.split('\n');

  // Simple LCS-based diff
  const origSet = new Set(origLines.map((l) => l.trim()));
  const optSet = new Set(optLines.map((l) => l.trim()));

  const origAnnotated = origLines.map((line) => ({
    line,
    type: optSet.has(line.trim()) ? 'same' : 'removed',
  }));

  const optAnnotated = optLines.map((line) => ({
    line,
    type: origSet.has(line.trim()) ? 'same' : 'added',
  }));

  return { origAnnotated, optAnnotated };
}

function DiffPane({
  lines,
  side,
}: {
  lines: { line: string; type: string }[];
  side: 'original' | 'optimized';
}) {
  return (
    <div className="overflow-x-auto">
      <pre className="text-xs code-font leading-6 p-4">
        {lines.map((entry, i) => {
          let lineClass = 'text-gray-300';
          let bgClass = '';
          if (entry.type === 'removed') {
            lineClass = 'text-red-300';
            bgClass = 'bg-red-500/10';
          } else if (entry.type === 'added') {
            lineClass = 'text-emerald-300';
            bgClass = 'bg-emerald-500/10';
          }
          const prefix =
            entry.type === 'removed' ? '- ' : entry.type === 'added' ? '+ ' : '  ';
          void side;
          return (
            <div key={i} className={`${bgClass} px-2 rounded-sm`}>
              <span className="select-none text-gray-600 w-6 inline-block mr-2">{i + 1}</span>
              <span
                className={`${
                  entry.type !== 'same' ? 'font-semibold' : ''
                } ${lineClass}`}
              >
                {prefix}
                {entry.line}
              </span>
            </div>
          );
        })}
      </pre>
    </div>
  );
}

export default function QueryDiff({ original, optimized }: QueryDiffProps) {
  const [view, setView] = useState<'diff' | 'editor'>('diff');

  if (!optimized || optimized.trim() === '') {
    return (
      <div className="bg-gray-800 border border-gray-700 rounded-xl p-8 text-center">
        <ArrowLeftRight className="w-10 h-10 text-gray-600 mx-auto mb-3" />
        <p className="text-gray-400 text-sm">No optimization was generated for this query.</p>
      </div>
    );
  }

  const { origAnnotated, optAnnotated } = computeDiff(original, optimized);

  return (
    <div className="space-y-3">
      {/* View toggle */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => setView('diff')}
          className={`text-xs px-3 py-1.5 rounded-md font-medium transition-colors ${
            view === 'diff'
              ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
              : 'text-gray-400 hover:text-gray-200 border border-gray-700'
          }`}
        >
          Diff View
        </button>
        <button
          onClick={() => setView('editor')}
          className={`text-xs px-3 py-1.5 rounded-md font-medium transition-colors ${
            view === 'editor'
              ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
              : 'text-gray-400 hover:text-gray-200 border border-gray-700'
          }`}
        >
          Editor View
        </button>
      </div>

      {view === 'diff' ? (
        <div className="grid grid-cols-2 gap-3">
          {/* Original */}
          <div className="bg-gray-900 border border-gray-700 rounded-lg overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-gray-700 bg-gray-800">
              <span className="text-xs font-semibold text-red-400 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-red-400 inline-block" />
                Original SQL
              </span>
              <CopyButton text={original} />
            </div>
            <DiffPane lines={origAnnotated} side="original" />
          </div>

          {/* Optimized */}
          <div className="bg-gray-900 border border-gray-700 rounded-lg overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-gray-700 bg-gray-800">
              <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400 inline-block" />
                Optimized SQL
              </span>
              <CopyButton text={optimized} />
            </div>
            <DiffPane lines={optAnnotated} side="optimized" />
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-red-400">Original SQL</span>
              <CopyButton text={original} />
            </div>
            <SqlEditor value={original} readOnly minHeight="300px" />
          </div>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-emerald-400">Optimized SQL</span>
              <CopyButton text={optimized} />
            </div>
            <SqlEditor value={optimized} readOnly minHeight="300px" />
          </div>
        </div>
      )}
    </div>
  );
}
