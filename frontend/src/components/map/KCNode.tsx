"use client";

import { Handle, Position } from "reactflow";
import { MasteryStatus } from "@/lib/types";

interface KCNodeData {
  label: string;
  status: MasteryStatus;
  pMastery: number;
  isCurrent: boolean;
  isOnRoute: boolean;
}

const statusColors: Record<MasteryStatus, string> = {
  locked: "bg-slate-200 border-slate-300 text-slate-500",
  available: "bg-blue-100 border-blue-400 text-blue-800",
  in_progress: "bg-amber-100 border-amber-400 text-amber-800",
  mastered: "bg-emerald-100 border-emerald-400 text-emerald-800",
};

const statusDots: Record<MasteryStatus, string> = {
  locked: "bg-slate-400",
  available: "bg-blue-400",
  in_progress: "bg-amber-400",
  mastered: "bg-emerald-400",
};

export default function KCNode({ data }: { data: KCNodeData }) {
  const { label, status, pMastery, isCurrent, isOnRoute } = data;

  return (
    <div
      className={`
        px-3 py-2 rounded-xl border-2 min-w-[140px] text-center shadow-sm relative
        ${statusColors[status]}
        ${isCurrent ? "ring-4 ring-blue-500 ring-offset-1 scale-105" : ""}
        ${isOnRoute && !isCurrent ? "border-dashed" : ""}
        transition-all duration-300
      `}
    >
      <Handle type="target" position={Position.Top} className="opacity-0" />
      <Handle type="source" position={Position.Bottom} className="opacity-0" />

      <div className="flex items-center justify-center gap-1.5 mb-1">
        <div className={`w-2 h-2 rounded-full ${statusDots[status]}`} />
        <span className="text-xs font-semibold">{label}</span>
      </div>

      {/* Mastery bar */}
      <div className="h-1.5 bg-slate-200/60 rounded-full overflow-hidden mt-1">
        <div
          className="h-full rounded-full mastery-bar-fill"
          style={{
            width: `${Math.round(pMastery * 100)}%`,
            backgroundColor:
              pMastery >= 0.95 ? "#10b981" : pMastery >= 0.5 ? "#f59e0b" : "#94a3b8",
          }}
        />
      </div>
      <div className="text-[10px] mt-0.5 opacity-70">{Math.round(pMastery * 100)}%</div>

      {isCurrent && (
        <div className="absolute -top-2 -right-2 bg-blue-600 text-white text-[9px] px-1.5 py-0.5 rounded-full font-bold">
          NOW
        </div>
      )}
    </div>
  );
}
