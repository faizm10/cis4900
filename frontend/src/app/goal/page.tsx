"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { KC } from "@/lib/types";
import { useLearnerStore } from "@/store/learnerStore";

export default function GoalPage() {
  const router = useRouter();
  const { learnerId, setGoal, setCurrentKc, setRoute } = useLearnerStore();
  const [kcs, setKcs] = useState<KC[]>([]);
  const [selected, setSelected] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!learnerId) { router.push("/"); return; }
    api.getKCs().then(setKcs).catch(() => setError("Failed to load concepts."));
  }, [learnerId, router]);

  async function handleStart() {
    if (!selected || !learnerId) return;
    setLoading(true);
    setError("");
    try {
      const route = await api.createRoute(learnerId, selected);
      const goal = kcs.find((k) => k.kc_id === selected);
      setGoal(selected, goal?.name ?? "");
      setRoute(route.ordered_kc_ids, route.ordered_kc_names);
      if (route.next_kc_id) setCurrentKc(route.next_kc_id);
      router.push("/map");
    } catch {
      setError("Failed to create route. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh]">
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8 w-full max-w-lg">
        <h1 className="text-xl font-bold text-slate-800 mb-2">Choose Your Learning Goal</h1>
        <p className="text-slate-500 text-sm mb-6">
          Select the CS concept you want to master. The system will map a personalized route from
          where you are now to that goal.
        </p>

        {error && (
          <div className="bg-red-50 text-red-700 text-sm rounded-lg px-4 py-3 mb-4">{error}</div>
        )}

        <div className="grid grid-cols-1 gap-2 mb-6 max-h-80 overflow-y-auto">
          {kcs.map((kc) => (
            <button
              key={kc.kc_id}
              onClick={() => setSelected(kc.kc_id)}
              className={`text-left px-4 py-3 rounded-lg border-2 transition-colors ${
                selected === kc.kc_id
                  ? "border-blue-500 bg-blue-50"
                  : "border-slate-200 hover:border-slate-300 bg-white"
              }`}
            >
              <div className="font-medium text-slate-800">{kc.name}</div>
              {kc.description && (
                <div className="text-xs text-slate-500 mt-0.5">{kc.description}</div>
              )}
            </button>
          ))}
        </div>

        <button
          onClick={handleStart}
          disabled={!selected || loading}
          className="w-full bg-blue-600 text-white py-2.5 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? "Creating route..." : "Generate My Learning Route →"}
        </button>
      </div>
    </div>
  );
}
