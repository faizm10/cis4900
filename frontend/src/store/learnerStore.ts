"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

interface LearnerStore {
  learnerId: string | null;
  goalKcId: number | null;
  currentKcId: number | null;
  routeKcIds: number[];
  routeKcNames: string[];
  goalKcName: string | null;
  setLearner: (id: string) => void;
  setGoal: (kcId: number, kcName: string) => void;
  setCurrentKc: (kcId: number) => void;
  setRoute: (kcIds: number[], kcNames: string[]) => void;
  reset: () => void;
}

export const useLearnerStore = create<LearnerStore>()(
  persist(
    (set) => ({
      learnerId: null,
      goalKcId: null,
      currentKcId: null,
      routeKcIds: [],
      routeKcNames: [],
      goalKcName: null,

      setLearner: (id) => set({ learnerId: id }),
      setGoal: (kcId, kcName) => set({ goalKcId: kcId, goalKcName: kcName }),
      setCurrentKc: (kcId) => set({ currentKcId: kcId }),
      setRoute: (kcIds, kcNames) => set({ routeKcIds: kcIds, routeKcNames: kcNames }),
      reset: () =>
        set({
          goalKcId: null,
          currentKcId: null,
          routeKcIds: [],
          routeKcNames: [],
          goalKcName: null,
        }),
    }),
    {
      name: "cs-learner-store",
    }
  )
);
