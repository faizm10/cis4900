"use client";

import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import { KC, Edge, ItemWithAnswer, AdminStats } from "@/lib/types";

type Tab = "kcs" | "items" | "edges" | "stats";

export default function AdminPage() {
  const [tab, setTab] = useState<Tab>("kcs");
  const [kcs, setKcs] = useState<KC[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [items, setItems] = useState<ItemWithAnswer[]>([]);
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [filterKcId, setFilterKcId] = useState<number | "">("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // New KC form
  const [newKcName, setNewKcName] = useState("");
  const [newKcDesc, setNewKcDesc] = useState("");

  // New Edge form
  const [newFrom, setNewFrom] = useState<number | "">("");
  const [newTo, setNewTo] = useState<number | "">("");

  // New Item form
  const [newItemKc, setNewItemKc] = useState<number | "">("");
  const [newItemPrompt, setNewItemPrompt] = useState("");
  const [newItemAnswer, setNewItemAnswer] = useState("");

  const loadAll = useCallback(async () => {
    try {
      const [k, e, i, s] = await Promise.all([
        api.getKCs(),
        api.getEdges(),
        api.getItems(),
        api.getStats(),
      ]);
      setKcs(k);
      setEdges(e);
      setItems(i);
      setStats(s);
    } catch {
      setError("Failed to load data. Is the backend running?");
    }
  }, []);

  useEffect(() => { loadAll(); }, [loadAll]);

  const showSuccess = (msg: string) => {
    setSuccess(msg);
    setTimeout(() => setSuccess(""), 3000);
  };

  async function handleAddKC(e: React.FormEvent) {
    e.preventDefault();
    if (!newKcName.trim()) return;
    try {
      await api.createKC({ name: newKcName.trim(), description: newKcDesc.trim() || null, p_l0: 0.1, p_t: 0.1, p_g: 0.25, p_s: 0.1 });
      setNewKcName(""); setNewKcDesc("");
      showSuccess("KC created.");
      loadAll();
    } catch { setError("Failed to create KC."); }
  }

  async function handleDeleteKC(kcId: number) {
    if (!confirm("Delete this KC and all its items and edges?")) return;
    try {
      await api.deleteKC(kcId);
      showSuccess("KC deleted.");
      loadAll();
    } catch { setError("Failed to delete KC."); }
  }

  async function handleAddEdge(e: React.FormEvent) {
    e.preventDefault();
    if (!newFrom || !newTo) return;
    try {
      await api.createEdge(Number(newFrom), Number(newTo));
      setNewFrom(""); setNewTo("");
      showSuccess("Edge created.");
      loadAll();
    } catch { setError("Failed to create edge."); }
  }

  async function handleDeleteEdge(edgeId: number) {
    try {
      await api.deleteEdge(edgeId);
      showSuccess("Edge deleted.");
      loadAll();
    } catch { setError("Failed to delete edge."); }
  }

  async function handleAddItem(e: React.FormEvent) {
    e.preventDefault();
    if (!newItemKc || !newItemPrompt.trim() || !newItemAnswer.trim()) return;
    try {
      await api.createItem({
        kc_id: Number(newItemKc),
        prompt: newItemPrompt.trim(),
        type: "multiple_choice",
        choices: [
          { label: "A", text: newItemAnswer.trim() },
          { label: "B", text: "Wrong answer 1" },
          { label: "C", text: "Wrong answer 2" },
          { label: "D", text: "Wrong answer 3" },
        ],
        answer: "A",
        difficulty: 0.5,
      });
      setNewItemPrompt(""); setNewItemAnswer("");
      showSuccess("Item created (answer is A, edit manually as needed).");
      loadAll();
    } catch { setError("Failed to create item."); }
  }

  async function handleDeleteItem(itemId: number) {
    try {
      await api.deleteItem(itemId);
      showSuccess("Item deleted.");
      loadAll();
    } catch { setError("Failed to delete item."); }
  }

  async function handleSeed() {
    try {
      const res = await api.runSeed();
      showSuccess(res.message);
      loadAll();
    } catch { setError("Failed to run seed."); }
  }

  const kcMap: Record<number, string> = {};
  kcs.forEach((k) => { kcMap[k.kc_id] = k.name; });

  const filteredItems = filterKcId ? items.filter((i) => i.kc_id === Number(filterKcId)) : items;

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-slate-800">Admin Panel</h1>
        <button onClick={handleSeed} className="text-sm px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-800">
          Re-seed Data
        </button>
      </div>

      {error && <div className="bg-red-50 text-red-700 text-sm rounded-lg px-4 py-3">{error}</div>}
      {success && <div className="bg-emerald-50 text-emerald-700 text-sm rounded-lg px-4 py-3">{success}</div>}

      {/* Tabs */}
      <div className="flex gap-1 border-b border-slate-200">
        {(["kcs", "items", "edges", "stats"] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm font-medium capitalize transition-colors border-b-2 -mb-px ${
              tab === t ? "border-blue-500 text-blue-600" : "border-transparent text-slate-500 hover:text-slate-700"
            }`}
          >
            {t === "kcs" ? "Knowledge Components" : t === "stats" ? "Analytics" : t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      {/* KCs tab */}
      {tab === "kcs" && (
        <div className="space-y-4">
          <form onSubmit={handleAddKC} className="bg-white rounded-xl border border-slate-200 p-4 flex gap-2 items-end">
            <div className="flex-1">
              <label className="block text-xs font-medium text-slate-600 mb-1">Name</label>
              <input value={newKcName} onChange={(e) => setNewKcName(e.target.value)}
                placeholder="e.g. Recursion" className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
            </div>
            <div className="flex-[2]">
              <label className="block text-xs font-medium text-slate-600 mb-1">Description</label>
              <input value={newKcDesc} onChange={(e) => setNewKcDesc(e.target.value)}
                placeholder="Optional description" className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
            </div>
            <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700">
              Add KC
            </button>
          </form>
          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="text-left px-4 py-2.5 font-medium text-slate-600">ID</th>
                  <th className="text-left px-4 py-2.5 font-medium text-slate-600">Name</th>
                  <th className="text-left px-4 py-2.5 font-medium text-slate-600">Description</th>
                  <th className="text-left px-4 py-2.5 font-medium text-slate-600">P(L0) / P(T) / P(G) / P(S)</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {kcs.map((kc) => (
                  <tr key={kc.kc_id} className="border-b border-slate-100 last:border-0">
                    <td className="px-4 py-2.5 text-slate-400">{kc.kc_id}</td>
                    <td className="px-4 py-2.5 font-medium text-slate-800">{kc.name}</td>
                    <td className="px-4 py-2.5 text-slate-500 text-xs max-w-xs truncate">{kc.description}</td>
                    <td className="px-4 py-2.5 text-slate-500 text-xs font-mono">
                      {kc.p_l0} / {kc.p_t} / {kc.p_g} / {kc.p_s}
                    </td>
                    <td className="px-4 py-2.5">
                      <button onClick={() => handleDeleteKC(kc.kc_id)}
                        className="text-xs text-red-500 hover:text-red-700">Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Items tab */}
      {tab === "items" && (
        <div className="space-y-4">
          <form onSubmit={handleAddItem} className="bg-white rounded-xl border border-slate-200 p-4 space-y-2">
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">KC</label>
                <select value={newItemKc} onChange={(e) => setNewItemKc(Number(e.target.value))}
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
                  <option value="">Select KC</option>
                  {kcs.map((k) => <option key={k.kc_id} value={k.kc_id}>{k.name}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">Correct Answer Text</label>
                <input value={newItemAnswer} onChange={(e) => setNewItemAnswer(e.target.value)}
                  placeholder="Text for the correct option (A)" className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
              </div>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Prompt</label>
              <textarea value={newItemPrompt} onChange={(e) => setNewItemPrompt(e.target.value)}
                rows={2} placeholder="Question text..." className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
            </div>
            <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700">
              Add Item
            </button>
          </form>

          <div className="flex items-center gap-2">
            <label className="text-sm text-slate-600">Filter by KC:</label>
            <select value={filterKcId} onChange={(e) => setFilterKcId(e.target.value ? Number(e.target.value) : "")}
              className="border border-slate-300 rounded-lg px-3 py-1.5 text-sm">
              <option value="">All KCs</option>
              {kcs.map((k) => <option key={k.kc_id} value={k.kc_id}>{k.name}</option>)}
            </select>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="text-left px-4 py-2.5 font-medium text-slate-600">KC</th>
                  <th className="text-left px-4 py-2.5 font-medium text-slate-600">Prompt</th>
                  <th className="text-left px-4 py-2.5 font-medium text-slate-600">Answer</th>
                  <th className="text-left px-4 py-2.5 font-medium text-slate-600">Diff</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {filteredItems.map((item) => (
                  <tr key={item.item_id} className="border-b border-slate-100 last:border-0">
                    <td className="px-4 py-2.5 text-slate-600 whitespace-nowrap">{kcMap[item.kc_id]}</td>
                    <td className="px-4 py-2.5 text-slate-700 max-w-xs">
                      <span className="line-clamp-2 text-xs">{item.prompt}</span>
                    </td>
                    <td className="px-4 py-2.5 font-mono text-xs text-emerald-700">{item.answer}</td>
                    <td className="px-4 py-2.5 text-slate-500 text-xs">{item.difficulty}</td>
                    <td className="px-4 py-2.5">
                      <button onClick={() => handleDeleteItem(item.item_id)}
                        className="text-xs text-red-500 hover:text-red-700">Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Edges tab */}
      {tab === "edges" && (
        <div className="space-y-4">
          <form onSubmit={handleAddEdge} className="bg-white rounded-xl border border-slate-200 p-4 flex gap-2 items-end">
            <div className="flex-1">
              <label className="block text-xs font-medium text-slate-600 mb-1">Prerequisite (from)</label>
              <select value={newFrom} onChange={(e) => setNewFrom(Number(e.target.value))}
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
                <option value="">Select KC</option>
                {kcs.map((k) => <option key={k.kc_id} value={k.kc_id}>{k.name}</option>)}
              </select>
            </div>
            <div className="text-slate-400 pb-2">→</div>
            <div className="flex-1">
              <label className="block text-xs font-medium text-slate-600 mb-1">Depends on (to)</label>
              <select value={newTo} onChange={(e) => setNewTo(Number(e.target.value))}
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
                <option value="">Select KC</option>
                {kcs.map((k) => <option key={k.kc_id} value={k.kc_id}>{k.name}</option>)}
              </select>
            </div>
            <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700">
              Add Edge
            </button>
          </form>
          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="text-left px-4 py-2.5 font-medium text-slate-600">Prerequisite</th>
                  <th className="px-4 py-2.5 text-slate-400">→</th>
                  <th className="text-left px-4 py-2.5 font-medium text-slate-600">Unlocks</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {edges.map((e) => (
                  <tr key={e.edge_id} className="border-b border-slate-100 last:border-0">
                    <td className="px-4 py-2.5 text-slate-700">{kcMap[e.from_kc_id]}</td>
                    <td className="px-4 py-2.5 text-slate-300 text-center">→</td>
                    <td className="px-4 py-2.5 text-slate-700">{kcMap[e.to_kc_id]}</td>
                    <td className="px-4 py-2.5">
                      <button onClick={() => handleDeleteEdge(e.edge_id)}
                        className="text-xs text-red-500 hover:text-red-700">Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Stats tab */}
      {tab === "stats" && stats && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white rounded-xl border border-slate-200 p-5 text-center">
              <div className="text-3xl font-bold text-slate-800">{stats.learner_count}</div>
              <div className="text-xs text-slate-500 mt-1">Unique Learners</div>
            </div>
            <div className="bg-white rounded-xl border border-slate-200 p-5 text-center">
              <div className="text-3xl font-bold text-slate-800">{stats.attempt_count}</div>
              <div className="text-xs text-slate-500 mt-1">Total Attempts</div>
            </div>
          </div>
          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="text-left px-4 py-2.5 font-medium text-slate-600">KC</th>
                  <th className="text-left px-4 py-2.5 font-medium text-slate-600">Learners</th>
                  <th className="text-left px-4 py-2.5 font-medium text-slate-600">Avg Mastery</th>
                </tr>
              </thead>
              <tbody>
                {stats.kc_stats.map((s) => (
                  <tr key={s.kc_id} className="border-b border-slate-100 last:border-0">
                    <td className="px-4 py-2.5 text-slate-700 font-medium">{s.kc_name}</td>
                    <td className="px-4 py-2.5 text-slate-500">{s.learner_count}</td>
                    <td className="px-4 py-2.5">
                      <div className="flex items-center gap-2">
                        <div className="h-1.5 w-24 bg-slate-100 rounded-full overflow-hidden">
                          <div className="h-full bg-blue-500 rounded-full" style={{ width: `${Math.round(s.avg_mastery * 100)}%` }} />
                        </div>
                        <span className="text-xs text-slate-500">{Math.round(s.avg_mastery * 100)}%</span>
                      </div>
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
