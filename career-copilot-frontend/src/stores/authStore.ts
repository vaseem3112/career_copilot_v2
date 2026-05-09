import { create } from "zustand";
import { persist } from "zustand/middleware";

interface User { id?: string; name: string; email: string; isVerified?: boolean; }

interface AuthState {
  token: string | null;
  user: User | null;
  isVerified: boolean;
  pendingEmail: string | null;
  setAuth: (token: string, user: User) => void;
  setPendingEmail: (email: string | null) => void;
  setVerified: (v: boolean) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      isVerified: false,
      pendingEmail: null,
      setAuth: (token, user) => set({ token, user, isVerified: true }),
      setPendingEmail: (email) => set({ pendingEmail: email }),
      setVerified: (v) => set({ isVerified: v }),
      logout: () => {
        set({ token: null, user: null, isVerified: false, pendingEmail: null });
        localStorage.removeItem("cc-auth");
      },
    }),
    { name: "cc-auth", partialize: (s) => ({ token: s.token, user: s.user, isVerified: s.isVerified }) }
  )
);
