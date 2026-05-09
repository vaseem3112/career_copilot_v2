import { create } from "zustand";
import { dashboardApi } from "@/lib/api";

interface DashboardStats {
  profileScore: number;
  atsScore: number;
  jobMatches: number;
  shortlistChance: number;
  recentJobs: { title: string; company: string; location: string; score: number }[];
  suggestedRoles: { name: string; score: number }[];
  resumeHealth: { atsScore: number; improvements: string[] } | null;
  recentActivity: { text: string; time: string }[];
}

interface DashboardState {
  stats: DashboardStats | null;
  loading: boolean;
  fetchStats: () => Promise<void>;
}

const empty: DashboardStats = {
  profileScore: 0, atsScore: 0, jobMatches: 0, shortlistChance: 0,
  recentJobs: [], suggestedRoles: [], resumeHealth: null, recentActivity: [],
};

export const useDashboardStore = create<DashboardState>((set) => ({
  stats: null,
  loading: false,

  fetchStats: async () => {
    set({ loading: true });
    try {
      const { data } = await dashboardApi.stats();
      const d = data.stats ?? data;
      set({
        stats: {
          profileScore:    d.profile_score    ?? d.profileScore    ?? 0,
          atsScore:        d.ats_score        ?? d.atsScore        ?? 0,
          jobMatches:      d.job_matches      ?? d.jobMatches      ?? 0,
          shortlistChance: d.shortlist_chance ?? d.shortlistChance ?? 0,
          recentJobs:      d.recent_jobs      ?? d.recentJobs      ?? [],
          suggestedRoles:  d.suggested_roles  ?? d.suggestedRoles  ?? [],
          resumeHealth:    d.resume_health    ?? d.resumeHealth    ?? null,
          recentActivity:  d.recent_activity  ?? d.recentActivity  ?? [],
        },
      });
    } catch (_) { set({ stats: empty }); }
    finally { set({ loading: false }); }
  },
}));
