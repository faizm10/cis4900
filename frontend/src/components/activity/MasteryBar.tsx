"use client";

interface MasteryBarProps {
  before: number;
  after: number;
  threshold?: number;
}

function getMasteryColor(p: number): string {
  if (p >= 0.95) return "#10b981"; // emerald
  if (p >= 0.7) return "#3b82f6";  // blue
  if (p >= 0.4) return "#f59e0b";  // amber
  return "#ef4444";                 // red
}

export default function MasteryBar({ before, after, threshold = 0.95 }: MasteryBarProps) {
  const pct = Math.round(after * 100);
  const color = getMasteryColor(after);
  const thresholdPct = Math.round(threshold * 100);

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-slate-500">
        <span>Estimated mastery P(L)</span>
        <span className="font-medium" style={{ color }}>
          {pct}%
          {after > before && (
            <span className="text-emerald-500 ml-1">▲ {Math.round((after - before) * 100)}%</span>
          )}
          {after < before && (
            <span className="text-red-400 ml-1">▼ {Math.round((before - after) * 100)}%</span>
          )}
        </span>
      </div>
      <div className="relative h-3 bg-slate-100 rounded-full overflow-visible">
        {/* Previous mastery marker */}
        <div
          className="absolute top-0 h-full bg-slate-200 rounded-full"
          style={{ width: `${Math.round(before * 100)}%` }}
        />
        {/* Current mastery fill */}
        <div
          className="absolute top-0 h-full rounded-full mastery-bar-fill"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
        {/* Threshold marker */}
        <div
          className="absolute top-[-2px] bottom-[-2px] w-0.5 bg-slate-600 z-10"
          style={{ left: `${thresholdPct}%` }}
        >
          <div className="absolute -top-4 left-1 text-[9px] text-slate-500 whitespace-nowrap">
            {thresholdPct}%
          </div>
        </div>
      </div>
    </div>
  );
}
