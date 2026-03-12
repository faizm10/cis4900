"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useLearnerStore } from "@/store/learnerStore";
import KnowledgeMap from "@/components/map/KnowledgeMap";

export default function MapPage() {
  const router = useRouter();
  const { learnerId, goalKcName, routeKcNames, currentKcId, routeKcIds } = useLearnerStore();

  useEffect(() => {
    if (!learnerId) router.push("/");
  }, [learnerId, router]);

  const currentIdx = routeKcIds.indexOf(currentKcId ?? -1);

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-800">Knowledge Map</h1>
          {goalKcName && (
            <p className="text-sm text-slate-500">
              Goal: <span className="font-medium text-blue-600">{goalKcName}</span>
            </p>
          )}
        </div>
        <div className="flex gap-2">
          <Link
            href="/goal"
            className="text-sm px-4 py-2 border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50"
          >
            Change Goal
          </Link>
          <Link
            href="/activity"
            className="text-sm px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
          >
            Start Practicing →
          </Link>
        </div>
      </div>

      {/* Route breadcrumb */}
      {routeKcNames.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 px-4 py-3">
          <p className="text-xs font-medium text-slate-500 mb-2 uppercase tracking-wide">Your Route</p>
          <div className="flex items-center gap-1 flex-wrap">
            {routeKcNames.map((name, i) => (
              <div key={i} className="flex items-center gap-1">
                <span
                  className={`text-sm px-2 py-0.5 rounded-full ${
                    i === currentIdx
                      ? "bg-blue-600 text-white font-medium"
                      : i < currentIdx
                      ? "bg-emerald-100 text-emerald-700 line-through"
                      : "bg-slate-100 text-slate-600"
                  }`}
                >
                  {name}
                </span>
                {i < routeKcNames.length - 1 && (
                  <span className="text-slate-300 text-xs">→</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="flex items-center gap-4 text-xs text-slate-500">
        {[
          { color: "bg-slate-300", label: "Locked" },
          { color: "bg-blue-400", label: "Available" },
          { color: "bg-amber-400", label: "In Progress" },
          { color: "bg-emerald-400", label: "Mastered" },
        ].map(({ color, label }) => (
          <div key={label} className="flex items-center gap-1.5">
            <div className={`w-3 h-3 rounded-full ${color}`} />
            <span>{label}</span>
          </div>
        ))}
      </div>

      <KnowledgeMap />
    </div>
  );
}
