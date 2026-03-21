import type {
  KC,
  GraphData,
  Edge,
  Item,
  ItemWithAnswer,
  MasteryResponse,
  MasteryEntry,
  AttemptSubmit,
  AttemptResponse,
  AttemptRecord,
  Route,
  AdminStats,
  TutorChatResponse,
} from "./types";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "Unknown error");
    throw new Error(`API ${res.status}: ${text}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  // KCs
  getKCs: () => request<KC[]>("/api/v1/kcs"),
  getKC: (kcId: number) => request<KC>(`/api/v1/kcs/${kcId}`),
  getGraph: () => request<GraphData>("/api/v1/kcs/graph"),
  createKC: (data: Omit<KC, "kc_id" | "created_ts">) =>
    request<KC>("/api/v1/kcs", { method: "POST", body: JSON.stringify(data) }),
  updateKC: (kcId: number, data: Partial<KC>) =>
    request<KC>(`/api/v1/kcs/${kcId}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteKC: (kcId: number) =>
    request<void>(`/api/v1/kcs/${kcId}`, { method: "DELETE" }),

  // Edges
  getEdges: () => request<Edge[]>("/api/v1/edges"),
  createEdge: (from_kc_id: number, to_kc_id: number) =>
    request<Edge>("/api/v1/edges", { method: "POST", body: JSON.stringify({ from_kc_id, to_kc_id }) }),
  deleteEdge: (edgeId: number) =>
    request<void>(`/api/v1/edges/${edgeId}`, { method: "DELETE" }),

  // Items
  getItems: (kcId?: number) =>
    request<ItemWithAnswer[]>(`/api/v1/items${kcId ? `?kc_id=${kcId}` : ""}`),
  getNextItem: (learnerId: string, kcId: number) =>
    request<Item>(`/api/v1/items/next?learner_id=${encodeURIComponent(learnerId)}&kc_id=${kcId}`),
  createItem: (data: Omit<ItemWithAnswer, "item_id">) =>
    request<ItemWithAnswer>("/api/v1/items", { method: "POST", body: JSON.stringify(data) }),
  updateItem: (itemId: number, data: Partial<ItemWithAnswer>) =>
    request<ItemWithAnswer>(`/api/v1/items/${itemId}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteItem: (itemId: number) =>
    request<void>(`/api/v1/items/${itemId}`, { method: "DELETE" }),

  // Attempts
  submitAttempt: (payload: AttemptSubmit) =>
    request<AttemptResponse>("/api/v1/attempts", { method: "POST", body: JSON.stringify(payload) }),
  getAttempts: (learnerId: string, kcId?: number, limit = 20) =>
    request<AttemptRecord[]>(
      `/api/v1/attempts?learner_id=${encodeURIComponent(learnerId)}${kcId ? `&kc_id=${kcId}` : ""}&limit=${limit}`
    ),

  // Mastery
  getMastery: (learnerId: string) =>
    request<MasteryResponse>(`/api/v1/mastery?learner_id=${encodeURIComponent(learnerId)}`),
  getMasteryForKC: (learnerId: string, kcId: number) =>
    request<MasteryEntry>(`/api/v1/mastery/${encodeURIComponent(learnerId)}/${kcId}`),
  resetMastery: (learnerId: string) =>
    request<void>(`/api/v1/mastery/${encodeURIComponent(learnerId)}`, { method: "DELETE" }),

  // Routes
  createRoute: (learnerId: string, goalKcId: number) =>
    request<Route>("/api/v1/routes", {
      method: "POST",
      body: JSON.stringify({ learner_id: learnerId, goal_kc_id: goalKcId }),
    }),
  getRoute: (learnerId: string) =>
    request<Route>(`/api/v1/routes/${encodeURIComponent(learnerId)}`),
  advanceRoute: (learnerId: string) =>
    request<Route>(`/api/v1/routes/${encodeURIComponent(learnerId)}/advance`, { method: "POST" }),
  rerouteRoute: (learnerId: string) =>
    request<Route>(`/api/v1/routes/${encodeURIComponent(learnerId)}/reroute`, { method: "POST" }),

  // Admin
  getStats: () => request<AdminStats>("/api/v1/admin/stats"),
  runSeed: () => request<{ message: string; kc_count: number }>("/api/v1/admin/seed", { method: "POST" }),

  // Tutor (optional; 503 if OPENAI_API_KEY unset)
  tutorChat: (payload: { learner_id: string; message?: string; kc_id?: number | null }) =>
    request<TutorChatResponse>("/api/v1/tutor/chat", {
      method: "POST",
      body: JSON.stringify({
        learner_id: payload.learner_id,
        message: payload.message ?? "",
        kc_id: payload.kc_id ?? null,
      }),
    }),
};
