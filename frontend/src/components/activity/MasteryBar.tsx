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
  const deltaPp = Math.round(Math.abs(after - before) * 100);

  return (
    <div className="space-y-1">
      <div className="flex justify-between items-center gap-3 text-xs text-slate-500">
        <span className="min-w-0">Estimated mastery P(L)</span>
        <span
          className="font-medium shrink-0 whitespace-nowrap text-right tabular-nums"
          style={{ color }}
        >
          {pct}%
          {after > before && (
            <span className="text-emerald-600 ml-1.5">▲ {deltaPp} pp</span>
          )}
          {after < before && (
            <span className="text-red-400 ml-1.5">▼ {deltaPp} pp</span>
          )}
        </span>
      </div>
      {/* pb-4 reserves space for the threshold label below the bar (was -top-4 and collided with the row above). */}
      <div className="relative pb-4">
        <div className="relative h-3 overflow-hidden rounded-full bg-slate-100">
          <div
            className="absolute top-0 h-full rounded-full bg-slate-200"
            style={{ width: `${Math.round(before * 100)}%` }}
          />
          <div
            className="absolute top-0 h-full rounded-full mastery-bar-fill"
            style={{ width: `${pct}%`, backgroundColor: color }}
          />
        </div>
        <div
          className="pointer-events-none absolute top-0 z-10 h-3 w-0.5 -translate-x-1/2 bg-slate-600"
          style={{ left: `${thresholdPct}%` }}
        />
        <div
          className="pointer-events-none absolute z-10 -translate-x-1/2 whitespace-nowrap text-[9px] text-slate-500"
          style={{ left: `${thresholdPct}%`, top: "calc(0.75rem + 2px)" }}
          title="Mastery threshold τ"
        >
          τ {thresholdPct}%
        </div>
      </div>
    </div>
  );
}
