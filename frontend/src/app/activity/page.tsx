"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import { AttemptResponse, Item } from "@/lib/types";
import { useLearnerStore } from "@/store/learnerStore";
import MasteryBar from "@/components/activity/MasteryBar";
import MultipleChoiceForm from "@/components/activity/MultipleChoiceForm";

type Phase = "loading" | "question" | "submitted" | "decision";

export default function ActivityPage() {
  const router = useRouter();
  const { learnerId, currentKcId, goalKcName, setCurrentKc, setRoute } =
    useLearnerStore();

  const [item, setItem] = useState<Item | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [result, setResult] = useState<AttemptResponse | null>(null);
  const [phase, setPhase] = useState<Phase>("loading");
  const [error, setError] = useState("");
  const [kcName, setKcName] = useState<string>("");
  const [modal, setModal] = useState<"advance" | "reroute" | "complete" | null>(null);

  const loadItem = useCallback(async () => {
    if (!learnerId || !currentKcId) return;
    setPhase("loading");
    setSelected(null);
    setResult(null);
    setError("");
    try {
      const [nextItem, kc] = await Promise.all([
        api.getNextItem(learnerId, currentKcId),
        api.getKC(currentKcId),
      ]);
      setItem(nextItem);
      setKcName(kc.name);
      setPhase("question");
    } catch {
      setError("Failed to load question. Is the backend running?");
      setPhase("question");
    }
  }, [learnerId, currentKcId]);

  useEffect(() => {
    if (!learnerId) { router.push("/"); return; }
    if (!currentKcId) { router.push("/goal"); return; }
    loadItem();
  }, [learnerId, currentKcId, router, loadItem]);

  async function handleSubmit() {
    if (!selected || !item || !learnerId || !currentKcId) return;
    setPhase("submitted");
    try {
      const res = await api.submitAttempt({
        learner_id: learnerId,
        item_id: item.item_id,
        kc_id: currentKcId,
        response: selected,
      });
      setResult(res);

      if (res.decision === "advance") {
        const route = await api.advanceRoute(learnerId);
        setRoute(route.ordered_kc_ids, route.ordered_kc_names);
        if (route.next_kc_id) {
          setCurrentKc(route.next_kc_id);
          setModal("advance");
        } else {
          setModal("complete");
        }
      } else if (res.decision === "reroute") {
        const route = await api.rerouteRoute(learnerId);
        setRoute(route.ordered_kc_ids, route.ordered_kc_names);
        if (route.next_kc_id) setCurrentKc(route.next_kc_id);
        setModal("reroute");
      }
    } catch {
      setError("Failed to submit answer.");
      setPhase("question");
    }
  }

  function handleNext() {
    setModal(null);
    loadItem();
  }

  if (!learnerId || !currentKcId) return null;

  return (
    <div className="max-w-2xl mx-auto space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-800">Practice</h1>
          <p className="text-sm text-slate-500">
            Topic: <span className="font-medium text-blue-600">{kcName || "Loading..."}</span>
            {goalKcName && (
              <span className="text-slate-400"> → Goal: {goalKcName}</span>
            )}
          </p>
        </div>
        <Link
          href="/map"
          className="text-sm px-3 py-1.5 border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50"
        >
          View Map
        </Link>
      </div>

      {error && (
        <div className="bg-red-50 text-red-700 text-sm rounded-lg px-4 py-3">{error}</div>
      )}

      {/* Question card */}
      {item && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-5">
          {/* Prompt */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-medium uppercase tracking-wide">
                {item.type === "multiple_choice" ? "Multiple Choice" : "Free Text"}
              </span>
              <span className="text-xs text-slate-400">
                Difficulty: {"⬛".repeat(Math.round(item.difficulty * 5)) + "⬜".repeat(5 - Math.round(item.difficulty * 5))}
              </span>
            </div>
            <pre className="whitespace-pre-wrap font-sans text-slate-800 text-sm leading-relaxed">
              {item.prompt}
            </pre>
          </div>

          {/* Choices */}
          {item.type === "multiple_choice" && item.choices && (
            <MultipleChoiceForm
              choices={item.choices}
              selected={selected}
              correctAnswer={result?.correct_answer ?? null}
              onSelect={setSelected}
              submitted={phase === "submitted"}
            />
          )}

          {/* Submit button */}
          {phase === "question" && (
            <button
              onClick={handleSubmit}
              disabled={!selected}
              className="w-full bg-blue-600 text-white py-2.5 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Submit Answer
            </button>
          )}

          {/* Feedback + mastery bar */}
          {result && (
            <div className="space-y-4 pt-2 border-t border-slate-100">
              <div
                className={`px-4 py-3 rounded-lg text-sm ${
                  result.correct
                    ? "bg-emerald-50 text-emerald-800 border border-emerald-200"
                    : "bg-red-50 text-red-800 border border-red-200"
                }`}
              >
                {result.correct ? "✓ " : "✗ "}{result.feedback}
              </div>
              <MasteryBar before={result.p_mastery_before} after={result.p_mastery_after} />
              {phase === "submitted" && !modal && (
                <button
                  onClick={handleNext}
                  className="w-full bg-slate-700 text-white py-2.5 rounded-lg font-medium hover:bg-slate-800 transition-colors"
                >
                  Next Question →
                </button>
              )}
            </div>
          )}

          {phase === "loading" && (
            <div className="text-center text-slate-400 text-sm py-4">Loading question...</div>
          )}
        </div>
      )}

      {phase === "loading" && !item && (
        <div className="bg-white rounded-2xl border border-slate-200 p-10 text-center text-slate-400">
          Loading question...
        </div>
      )}

      {/* Decision modals */}
      {modal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl shadow-xl p-8 max-w-sm w-full mx-4 text-center">
            {modal === "advance" && (
              <>
                <div className="text-4xl mb-3">🎉</div>
                <h2 className="text-lg font-bold text-slate-800 mb-2">KC Mastered!</h2>
                <p className="text-slate-500 text-sm mb-5">
                  You&apos;ve mastered <strong>{kcName}</strong>. Moving to the next topic on your route.
                </p>
              </>
            )}
            {modal === "reroute" && (
              <>
                <div className="text-4xl mb-3">🔄</div>
                <h2 className="text-lg font-bold text-slate-800 mb-2">Let&apos;s Reinforce a Prerequisite</h2>
                <p className="text-slate-500 text-sm mb-5">
                  You&apos;re having trouble with <strong>{kcName}</strong>. The system has rerouted you to
                  review a prerequisite concept first.
                </p>
              </>
            )}
            {modal === "complete" && (
              <>
                <div className="text-4xl mb-3">🏆</div>
                <h2 className="text-lg font-bold text-slate-800 mb-2">Goal Achieved!</h2>
                <p className="text-slate-500 text-sm mb-5">
                  You&apos;ve mastered your goal: <strong>{goalKcName}</strong>. Excellent work!
                </p>
              </>
            )}
            <div className="flex gap-2">
              {modal === "complete" ? (
                <Link
                  href="/progress"
                  className="flex-1 bg-blue-600 text-white py-2.5 rounded-lg font-medium hover:bg-blue-700 text-center"
                >
                  View Progress
                </Link>
              ) : (
                <button
                  onClick={handleNext}
                  className="flex-1 bg-blue-600 text-white py-2.5 rounded-lg font-medium hover:bg-blue-700"
                >
                  Continue →
                </button>
              )}
              <Link
                href="/map"
                className="flex-1 border border-slate-200 text-slate-700 py-2.5 rounded-lg font-medium hover:bg-slate-50 text-center"
              >
                View Map
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
