"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import { AttemptRecord, MasteryEntry, MasteryStatus } from "@/lib/types";
import { useLearnerStore } from "@/store/learnerStore";

const statusColors: Record<MasteryStatus, string> = {
  locked: "bg-slate-100 text-slate-500 border-slate-200",
  available: "bg-blue-50 text-blue-700 border-blue-200",
  in_progress: "bg-amber-50 text-amber-700 border-amber-200",
  mastered: "bg-emerald-50 text-emerald-700 border-emerald-200",
};

const statusLabels: Record<MasteryStatus, string> = {
  locked: "Locked",
  available: "Available",
  in_progress: "In Progress",
  mastered: "Mastered",
};

function getMasteryColor(p: number): string {
  if (p >= 0.95) return "#10b981";
  if (p >= 0.7) return "#3b82f6";
  if (p >= 0.4) return "#f59e0b";
  return "#ef4444";
}

export default function ProgressPage() {
  const router = useRouter();
  const { learnerId, goalKcName, reset } = useLearnerStore();
  const [masteries, setMasteries] = useState<MasteryEntry[]>([]);
  const [attempts, setAttempts] = useState<AttemptRecord[]>([]);
  const [resetting, setResetting] = useState(false);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    if (!learnerId) return;
    try {
      const [masteryRes, attemptsRes] = await Promise.all([
        api.getMastery(learnerId),
        api.getAttempts(learnerId, undefined, 30),
      ]);
      setMasteries(masteryRes.masteries);
      setAttempts(attemptsRes);
    } catch {
      setError("Failed to load progress. Is the backend running?");
    }
  }, [learnerId]);

  useEffect(() => {
    if (!learnerId) { router.push("/"); return; }
    load();
  }, [learnerId, router, load]);

  async function handleReset() {
    if (!learnerId || !confirm("Reset all progress? This cannot be undone.")) return;
    setResetting(true);
    try {
      await api.resetMastery(learnerId);
      reset();
      await load();
      router.push("/goal");
    } catch {
      setError("Failed to reset progress.");
    } finally {
      setResetting(false);
    }
  }

  const sortedMasteries = [...masteries].sort((a, b) => {
    const order: Record<MasteryStatus, number> = { mastered: 0, in_progress: 1, available: 2, locked: 3 };
    return order[a.status] - order[b.status];
  });

  const masteredCount = masteries.filter((m) => m.status === "mastered").length;
  const totalAttempts = attempts.length;
  const correctCount = attempts.filter((a) => a.correctness).length;

  const kcNameMap: Record<number, string> = {};
  masteries.forEach((m) => { kcNameMap[m.kc_id] = m.kc_name; });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-800">My Progress</h1>
          {goalKcName && (
            <p className="text-sm text-slate-500">
              Goal: <span className="font-medium text-blue-600">{goalKcName}</span>
            </p>
          )}
        </div>
        <div className="flex gap-2">
          <Link href="/activity" className="text-sm px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium">
            Continue →
          </Link>
          <button
            onClick={handleReset}
            disabled={resetting}
            className="text-sm px-4 py-2 border border-red-200 text-red-600 rounded-lg hover:bg-red-50 disabled:opacity-50"
          >
            {resetting ? "Resetting..." : "Reset Progress"}
          </button>
        </div>
      </div>

      {error && <div className="bg-red-50 text-red-700 text-sm rounded-lg px-4 py-3">{error}</div>}

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: "KCs Mastered", value: `${masteredCount} / ${masteries.length}` },
          { label: "Total Attempts", value: totalAttempts },
          { label: "Accuracy", value: totalAttempts > 0 ? `${Math.round((correctCount / totalAttempts) * 100)}%` : "—" },
        ].map(({ label, value }) => (
          <div key={label} className="bg-white rounded-xl border border-slate-200 p-4 text-center">
            <div className="text-2xl font-bold text-slate-800">{value}</div>
            <div className="text-xs text-slate-500 mt-1">{label}</div>
          </div>
        ))}
      </div>

      {/* Mastery grid */}
      <div>
        <h2 className="text-sm font-semibold text-slate-700 mb-3 uppercase tracking-wide">Knowledge Components</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {sortedMasteries.map((m) => (
            <div
              key={m.kc_id}
              className={`bg-white rounded-xl border-2 p-4 ${statusColors[m.status]}`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-sm">{m.kc_name}</span>
                <span className={`text-xs px-2 py-0.5 rounded-full border ${statusColors[m.status]}`}>
                  {statusLabels[m.status]}
                </span>
              </div>
              <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full mastery-bar-fill"
                  style={{
                    width: `${Math.round(m.p_mastery * 100)}%`,
                    backgroundColor: getMasteryColor(m.p_mastery),
                  }}
                />
              </div>
              <div className="flex justify-between text-xs text-slate-500 mt-1">
                <span>{Math.round(m.p_mastery * 100)}% mastery</span>
                <span>{m.attempt_count} attempts</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Attempt history */}
      {attempts.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold text-slate-700 mb-3 uppercase tracking-wide">Recent Attempts</h2>
          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="text-left px-4 py-2.5 font-medium text-slate-600">Topic</th>
                  <th className="text-left px-4 py-2.5 font-medium text-slate-600">Result</th>
                  <th className="text-left px-4 py-2.5 font-medium text-slate-600">Time</th>
                </tr>
              </thead>
              <tbody>
                {attempts.map((a) => (
                  <tr key={a.attempt_id} className="border-b border-slate-100 last:border-0">
                    <td className="px-4 py-2.5 text-slate-700">{kcNameMap[a.kc_id] ?? `KC ${a.kc_id}`}</td>
                    <td className="px-4 py-2.5">
                      <span className={a.correctness ? "text-emerald-600 font-medium" : "text-red-500"}>
                        {a.correctness ? "✓ Correct" : "✗ Incorrect"}
                      </span>
                    </td>
                    <td className="px-4 py-2.5 text-slate-400 text-xs">
                      {new Date(a.timestamp).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
