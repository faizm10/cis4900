"use client";

import { useState } from "react";
import { api } from "@/lib/api";

interface TutorPanelProps {
  learnerId: string;
  kcId: number | null;
}

export default function TutorPanel({ learnerId, kcId }: TutorPanelProps) {
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [reply, setReply] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSend() {
    setLoading(true);
    setError("");
    setReply(null);
    try {
      const res = await api.tutorChat({
        learner_id: learnerId,
        message: message.trim(),
        kc_id: kcId ?? undefined,
      });
      setReply(res.reply);
    } catch (e) {
      const text = e instanceof Error ? e.message : "Request failed";
      setError(
        text.includes("503")
          ? "AI tutor is not configured (set LLM_PROVIDER and the matching API key on the server)."
          : text
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between px-4 py-3 text-left text-sm font-medium text-slate-700 hover:bg-slate-50"
      >
        <span>AI tutor (optional)</span>
        <span className="text-slate-400">{open ? "▾" : "▸"}</span>
      </button>
      {open && (
        <div className="px-4 pb-4 space-y-3 border-t border-slate-100">
          <p className="text-xs text-slate-500 pt-3 leading-relaxed">
            Explanations only — the app still decides your path and mastery. Requires{" "}
            <code className="bg-slate-100 px-1 rounded">LLM_PROVIDER</code> + provider key (see README).
          </p>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Ask a question, or leave blank for a quick focus tip…"
            rows={3}
            className="w-full text-sm border border-slate-200 rounded-lg px-3 py-2 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="button"
            onClick={handleSend}
            disabled={loading}
            className="text-sm bg-slate-800 text-white px-4 py-2 rounded-lg hover:bg-slate-900 disabled:opacity-50"
          >
            {loading ? "Thinking…" : "Get help"}
          </button>
          {error && <p className="text-xs text-red-600">{error}</p>}
          {reply && (
            <div className="text-sm text-slate-700 bg-slate-50 rounded-lg p-3 whitespace-pre-wrap">
              {reply}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
