import { create } from "zustand";
import { jobsApi } from "@/lib/api";

export interface Job {
  id: string; title: string; company: string; location: string;
  salary?: string; posted?: string; matchScore?: number;
  description?: string; requirements?: string[]; type?: string;
  domain?: string; experience?: string; isSaved?: boolean;
}

interface JobFilters { page: number; limit: number; domain: string; location: string; experience: string; }

interface JobState {
  jobs: Job[];
  matched: Job[];
  saved: Job[];
  total: number;
  filters: JobFilters;
  loading: boolean;
  tab: "all" | "best" | "saved";
  fetchJobs: () => Promise<void>;
  fetchMatched: () => Promise<void>;
  fetchSaved: () => Promise<void>;
  saveJob: (id: string) => Promise<void>;
  unsaveJob: (id: string) => Promise<void>;
  setFilter: (k: keyof JobFilters, v: string | number) => void;
  setTab: (t: "all" | "best" | "saved") => void;
}

export const useJobStore = create<JobState>((set, get) => ({
  jobs: [], matched: [], saved: [],
  total: 0, loading: false,
  tab: "all",
  filters: { page: 1, limit: 20, domain: "", location: "", experience: "" },

  fetchJobs: async () => {
    set({ loading: true });
    try {
      const { filters } = get();
      const { data } = await jobsApi.list(filters);
      set({ jobs: data.jobs ?? data, total: data.total ?? (data.jobs ?? data).length });
    } finally { set({ loading: false }); }
  },

  fetchMatched: async () => {
    set({ loading: true });
    try {
      const { data } = await jobsApi.matched();
      set({ matched: data.jobs ?? data });
    } finally { set({ loading: false }); }
  },

  fetchSaved: async () => {
    try {
      const { data } = await jobsApi.saved();
      set({ saved: data.jobs ?? data });
    } catch (_) {}
  },

  saveJob: async (id) => {
    await jobsApi.save(id);
    set((s) => ({
      jobs: s.jobs.map((j) => j.id === id ? { ...j, isSaved: true } : j),
      matched: s.matched.map((j) => j.id === id ? { ...j, isSaved: true } : j),
    }));
  },

  unsaveJob: async (id) => {
    await jobsApi.unsave(id);
    set((s) => ({
      jobs: s.jobs.map((j) => j.id === id ? { ...j, isSaved: false } : j),
      matched: s.matched.map((j) => j.id === id ? { ...j, isSaved: false } : j),
      saved: s.saved.filter((j) => j.id !== id),
    }));
  },

  setFilter: (k, v) => set((s) => ({ filters: { ...s.filters, [k]: v } })),
  setTab: (tab) => set({ tab }),
}));
