import { create } from "zustand";
import { resumeApi } from "@/lib/api";

export interface Resume {
  id: string; filename: string; uploadedAt: string;
  atsScore?: number; type: "uploaded" | "generated"; status?: string;
}

interface ResumeState {
  resumes: Resume[];
  activeResumeId: string | null;
  loading: boolean;
  uploading: boolean;
  uploadProgress: number;
  fetchResumes: () => Promise<void>;
  uploadResume: (file: File) => Promise<Resume>;
  deleteResume: (id: string) => Promise<void>;
  analyzeResume: (id: string) => Promise<void>;
  setActive: (id: string | null) => void;
}

export const useResumeStore = create<ResumeState>((set, get) => ({
  resumes: [],
  activeResumeId: null,
  loading: false,
  uploading: false,
  uploadProgress: 0,

  fetchResumes: async () => {
    set({ loading: true });
    try {
      const { data } = await resumeApi.list();
      // backend returns { resumes: [...] } or just [...]
      set({ resumes: data.resumes ?? data });
    } finally { set({ loading: false }); }
  },

  uploadResume: async (file: File) => {
    set({ uploading: true, uploadProgress: 0 });
    try {
      const { data } = await resumeApi.upload(file, (pct) => set({ uploadProgress: pct }));
      const resume = data.resume ?? data;
      set((s) => ({ resumes: [resume, ...s.resumes] }));
      return resume;
    } finally { set({ uploading: false, uploadProgress: 0 }); }
  },

  deleteResume: async (id: string) => {
    await resumeApi.delete(id);
    set((s) => ({ resumes: s.resumes.filter((x) => x.id !== id) }));
  },

  analyzeResume: async (id: string) => {
    await resumeApi.analyze(id);
  },

  setActive: (activeResumeId) => set({ activeResumeId }),
}));
