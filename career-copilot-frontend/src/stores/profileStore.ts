import { create } from "zustand";
import { profileApi } from "@/lib/api";

interface Profile {
  name?: string; email?: string; phone?: string; city?: string;
  country?: string; linkedin?: string; github?: string; summary?: string;
  education?: any[]; experience?: any[]; skills?: string[];
  certifications?: any[]; projects?: any[];
  preferredRoles?: string[]; preferredLocations?: string[];
  salaryMin?: number; salaryMax?: number;
}

interface ProfileState {
  profile: Profile | null;
  completionScore: number;
  loading: boolean;
  setProfile: (p: Profile) => void;
  setCompletion: (n: number) => void;
  fetchProfile: () => Promise<void>;
  fetchCompletion: () => Promise<void>;
  updateProfile: (data: Partial<Profile>) => Promise<void>;
}

export const useProfileStore = create<ProfileState>((set, get) => ({
  profile: null,
  completionScore: 0,
  loading: false,
  setProfile: (profile) => set({ profile }),
  setCompletion: (completionScore) => set({ completionScore }),

  fetchProfile: async () => {
    set({ loading: true });
    try {
      const { data } = await profileApi.get();
      set({ profile: data });
    } catch (_) {}
    finally { set({ loading: false }); }
  },

  fetchCompletion: async () => {
    try {
      const { data } = await profileApi.completion();
      set({ completionScore: data.completion_score ?? data.score ?? 0 });
    } catch (_) {}
  },

  updateProfile: async (updates) => {
    const { data } = await profileApi.update(updates);
    set({ profile: data });
  },
}));
