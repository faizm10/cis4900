export interface KC {
  kc_id: number;
  name: string;
  description: string | null;
  p_l0: number;
  p_t: number;
  p_g: number;
  p_s: number;
  created_ts: string;
}

export interface Edge {
  edge_id: number;
  from_kc_id: number;
  to_kc_id: number;
}

export interface GraphData {
  kcs: KC[];
  edges: Edge[];
}

export interface Choice {
  label: string;
  text: string;
}

export interface Item {
  item_id: number;
  kc_id: number;
  prompt: string;
  type: "multiple_choice" | "free_text";
  choices: Choice[] | null;
  difficulty: number;
}

export interface ItemWithAnswer extends Item {
  answer: string;
}

export type MasteryStatus = "locked" | "available" | "in_progress" | "mastered";

export interface MasteryEntry {
  kc_id: number;
  kc_name: string;
  p_mastery: number;
  attempt_count: number;
  status: MasteryStatus;
  updated_ts: string | null;
}

export interface MasteryResponse {
  learner_id: string;
  masteries: MasteryEntry[];
}

export interface AttemptSubmit {
  learner_id: string;
  item_id: number;
  kc_id: number;
  response: string;
}

export interface AttemptResponse {
  attempt_id: number;
  correct: boolean;
  correct_answer: string;
  p_mastery_before: number;
  p_mastery_after: number;
  decision: "advance" | "remediate" | "reroute";
  next_kc_id: number | null;
  feedback: string;
}

export interface AttemptRecord {
  attempt_id: number;
  learner_id: string;
  item_id: number;
  kc_id: number;
  correctness: boolean;
  timestamp: string;
}

export interface Route {
  route_id: number;
  learner_id: string;
  goal_kc_id: number;
  goal_kc_name: string;
  ordered_kc_ids: number[];
  ordered_kc_names: string[];
  next_kc_id: number | null;
  next_kc_name: string | null;
  created_ts: string;
  updated_ts: string;
}

export interface AdminStats {
  learner_count: number;
  attempt_count: number;
  kc_stats: {
    kc_id: number;
    kc_name: string;
    learner_count: number;
    avg_mastery: number;
  }[];
}
