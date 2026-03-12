"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useLearnerStore } from "@/store/learnerStore";

export default function LandingPage() {
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const { setLearner, learnerId } = useLearnerStore();
  const router = useRouter();

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = name.trim();
    if (!trimmed) {
      setError("Please enter your name.");
      return;
    }
    const id = trimmed.toLowerCase().replace(/\s+/g, "_");
    setLearner(id);
    router.push("/goal");
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh]">
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-10 w-full max-w-md">
        <div className="text-center mb-8">
          <div className="text-5xl mb-4">🗺️</div>
          <h1 className="text-2xl font-bold text-slate-800 mb-2">CS Learning Map</h1>
          <p className="text-slate-500 text-sm leading-relaxed">
            An adaptive learning system that tracks your progress through CS concepts
            and generates a personalized learning route — like Google Maps, but for programming.
          </p>
        </div>

        {learnerId ? (
          <div className="space-y-3">
            <p className="text-center text-slate-600">
              Welcome back, <span className="font-semibold text-blue-600">{learnerId}</span>
            </p>
            <button
              onClick={() => router.push("/map")}
              className="w-full bg-blue-600 text-white py-2.5 rounded-lg font-medium hover:bg-blue-700 transition-colors"
            >
              Continue Learning
            </button>
            <button
              onClick={() => router.push("/goal")}
              className="w-full bg-white text-slate-700 py-2.5 rounded-lg font-medium border border-slate-200 hover:bg-slate-50 transition-colors"
            >
              Change Goal
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Your name
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => { setName(e.target.value); setError(""); }}
                placeholder="e.g. Alice"
                className="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              {error && <p className="text-red-500 text-xs mt-1">{error}</p>}
            </div>
            <button
              type="submit"
              className="w-full bg-blue-600 text-white py-2.5 rounded-lg font-medium hover:bg-blue-700 transition-colors"
            >
              Start Learning →
            </button>
          </form>
        )}
      </div>

      <div className="mt-8 grid grid-cols-3 gap-4 w-full max-w-md text-center text-sm text-slate-500">
        <div className="bg-white rounded-xl p-4 border border-slate-200">
          <div className="text-2xl mb-1">🧠</div>
          <p className="font-medium text-slate-700">Bayesian Tracking</p>
          <p className="text-xs">Probabilistic mastery model per concept</p>
        </div>
        <div className="bg-white rounded-xl p-4 border border-slate-200">
          <div className="text-2xl mb-1">🔀</div>
          <p className="font-medium text-slate-700">Smart Routing</p>
          <p className="text-xs">Prerequisite-aware learning paths</p>
        </div>
        <div className="bg-white rounded-xl p-4 border border-slate-200">
          <div className="text-2xl mb-1">🎯</div>
          <p className="font-medium text-slate-700">Adaptive</p>
          <p className="text-xs">Reroutes when you get stuck</p>
        </div>
      </div>
    </div>
  );
}
