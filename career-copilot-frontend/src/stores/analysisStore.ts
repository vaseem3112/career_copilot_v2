import { create } from "zustand";
import { analysisApi, atsApi } from "@/lib/api";

export interface AnalysisResult {
  id: string; resumeId: string; shortlistProbability: number;
  summary: string; tags: string[]; detectedSkills: string[];
  suggestedRoles: { name: string; score: number; reason: string }[];
  strengths: string[]; weaknesses: string[]; missingSkills: string[];
  haveSkills: string[]; needSkills: string[];
  improvementPlan: string[]; resumePreview: string;
}

export interface ATSResult {
  atsScore: number; matchedKeywords: string[];
  missingKeywords: string[]; content: string;
}

interface AnalysisState {
  result: AnalysisResult | null;
  loading: boolean;
  error: string | null;
  atsResult: ATSResult | null;
  atsLoading: boolean;
  fetchAnalysis: (resumeId: string) => Promise<void>;
  generateATS: (payload: { resumeId: string; title: string; company?: string; jd: string }) => Promise<void>;
  reset: () => void;
}

export const useAnalysisStore = create<AnalysisState>((set) => ({
  result: null, loading: false, error: null,
  atsResult: null, atsLoading: false,

  fetchAnalysis: async (resumeId: string) => {
    if (!resumeId) { set({ error: "No resume selected" }); return; }
    set({ loading: true, error: null });
    try {
      const { data } = await analysisApi.get(resumeId);
      // Normalize backend snake_case → camelCase
      const r = data.analysis ?? data;
      set({
        result: {
          id:                   r.id,
          resumeId:             r.resume_id ?? resumeId,
          shortlistProbability: r.shortlist_probability ?? r.shortlistProbability ?? 0,
          summary:              r.profile_summary ?? r.summary ?? "",
          tags:                 r.domains ?? r.tags ?? [],
          detectedSkills:       r.skills ?? r.detectedSkills ?? [],
          suggestedRoles:       (r.suggested_roles ?? r.suggestedRoles ?? []).map((x: any) => ({
            name:   x.role ?? x.name,
            score:  x.match_score ?? x.score,
            reason: x.reason,
          })),
          strengths:        r.resume_analysis?.strengths ?? r.strengths ?? [],
          weaknesses:       r.resume_analysis?.weaknesses ?? r.weaknesses ?? [],
          missingSkills:    r.resume_analysis?.missing_skills ?? r.missingSkills ?? [],
          haveSkills:       r.skill_gap?.matched ?? r.haveSkills ?? [],
          needSkills:       r.skill_gap?.missing ?? r.needSkills ?? [],
          improvementPlan:  r.skill_gap?.suggestions ?? r.improvementPlan ?? [],
          resumePreview:    r.ats_resume ?? r.resumePreview ?? "",
        },
      });
    } catch (e: any) {
      set({ error: e?.response?.data?.message ?? e.message ?? "Analysis failed" });
    } finally { set({ loading: false }); }
  },

  generateATS: async (payload) => {
    set({ atsLoading: true, error: null, atsResult: null });
    try {
      const { data } = await atsApi.generate({
        resume_id:        payload.resumeId,
        target_job_title: payload.title,
        company:          payload.company,
        job_description:  payload.jd,
      });
      const r = data.ats ?? data;
      set({
        atsResult: {
          atsScore:        r.ats_score ?? r.atsScore ?? 0,
          matchedKeywords: r.matched_keywords ?? r.matchedKeywords ?? [],
          missingKeywords: r.missing_keywords ?? r.missingKeywords ?? [],
          content:         r.ats_resume ?? r.content ?? "",
        },
      });
    } catch (e: any) {
      set({ error: e?.response?.data?.message ?? e.message ?? "Generation failed" });
    } finally { set({ atsLoading: false }); }
  },

  reset: () => set({ result: null, atsResult: null, error: null }),
}));
