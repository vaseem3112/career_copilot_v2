import axios from "axios";
import { useAuthStore } from "@/stores/authStore";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:5000/api/v1",
  timeout: 30000,
});

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) useAuthStore.getState().logout();
    return Promise.reject(err);
  }
);

export const authApi = {
  register:       (d: { name: string; email: string; password: string }) => api.post("/auth/register", d),
  verifyOtp:      (d: { email: string; otp: string })                    => api.post("/auth/verify-otp", d),
  resendOtp:      (d: { email: string })                                  => api.post("/auth/resend-otp", d),
  login:          (d: { email: string; password: string })                => api.post("/auth/login", d),
  forgotPassword: (d: { email: string })                                  => api.post("/auth/forgot-password", d),
  resetPassword:  (d: { token: string; new_password: string })            => api.post("/auth/reset-password", d),
  logout:         ()                                                       => api.post("/auth/logout"),
};

export const profileApi = {
  get:        () => api.get("/profile"),
  update:     (d: object) => api.patch("/profile", d),
  completion: () => api.get("/profile/completion"),
};

export const resumeApi = {
  list:    () => api.get("/resume/list"),
  upload:  (file: File, onProgress?: (pct: number) => void) => {
    const fd = new FormData();
    fd.append("resume", file);
    return api.post("/parser/upload", fd, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: (e) => {
        if (e.total && onProgress) onProgress(Math.round((e.loaded / e.total) * 100));
      },
    });
  },
  delete:  (id: string) => api.delete(`/resume/${id}`),
  analyze: (resumeId: string) => api.post(`/parser/analyze/${resumeId}`),
};

export const analysisApi = {
  get: (resumeId: string) => api.get(`/analysis/${resumeId}`),
};

export const atsApi = {
  generate: (d: { resume_id: string; target_job_title: string; company?: string; job_description: string }) =>
    api.post("/ats/generate", d),
  score: (resumeId: string) => api.get(`/ats/score/${resumeId}`),
};

export const jobsApi = {
  list:    (params?: { page?: number; limit?: number; domain?: string; location?: string; experience?: string }) =>
    api.get("/jobs", { params }),
  matched: () => api.get("/match/jobs"),
  saved:   () => api.get("/jobs/saved"),
  save:    (jobId: string) => api.post(`/jobs/save/${jobId}`),
  unsave:  (jobId: string) => api.delete(`/jobs/save/${jobId}`),
};

export const dashboardApi = {
  stats: () => api.get("/dashboard/stats"),
};

export const notificationsApi = {
  list:    () => api.get("/notifications"),
  read:    (id: string) => api.patch(`/notifications/${id}/read`),
  readAll: () => api.patch("/notifications/read-all"),
};

export const settingsApi = {
  get:            () => api.get("/settings"),
  update:         (d: object) => api.patch("/settings", d),
  deleteAccount:  () => api.delete("/auth/account"),
  changePassword: (d: { current_password: string; new_password: string }) => api.patch("/settings/password", d),
  downloadData:   () => api.get("/settings/export", { responseType: "blob" }),
};
