import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Logo } from "@/components/Logo";
import { useAuthStore } from "@/stores/authStore";
import { authApi } from "@/lib/api";
import { Eye, EyeOff, Mail, Loader2 } from "lucide-react";
import { toast } from "sonner";

type Step = "register" | "login" | "verify" | "forgot";

export default function Auth() {
  const [params] = useSearchParams();
  const [step, setStep] = useState<Step>(params.get("mode") === "register" ? "register" : "login");
  const [showPwd, setShowPwd] = useState(false);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({ name: "", email: "", password: "", confirm: "" });
  const [otp, setOtp] = useState(["", "", "", "", "", ""]);
  const [cooldown, setCooldown] = useState(0);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const navigate = useNavigate();
  const { setAuth, setPendingEmail, pendingEmail } = useAuthStore();

  const f = (k: string, v: string) => { setForm((p) => ({ ...p, [k]: v })); setFieldErrors((p) => ({ ...p, [k]: "" })); };

  const startCooldown = () => {
    setCooldown(60);
    const t = setInterval(() => setCooldown((c) => { if (c <= 1) { clearInterval(t); return 0; } return c - 1; }), 1000);
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    const errs: Record<string, string> = {};
    if (!form.name.trim()) errs.name = "Name is required";
    if (!form.email.trim()) errs.email = "Email is required";
    if (form.password.length < 8) errs.password = "Minimum 8 characters";
    if (form.password !== form.confirm) errs.confirm = "Passwords don't match";
    if (Object.keys(errs).length) { setFieldErrors(errs); return; }
    setLoading(true);
    try {
      await authApi.register({ name: form.name, email: form.email, password: form.password });
      setPendingEmail(form.email);
      setStep("verify");
      startCooldown();
      toast.success("OTP sent to your email");
    } catch (e: any) {
      toast.error(e?.response?.data?.message ?? "Registration failed");
    } finally { setLoading(false); }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const { data } = await authApi.login({ email: form.email, password: form.password });
      setAuth(data.token, data.user);
      toast.success("Welcome back!");
      navigate("/dashboard");
    } catch (e: any) {
      const msg = e?.response?.data?.message ?? "Invalid credentials";
      setFieldErrors({ email: msg });
      toast.error(msg);
    } finally { setLoading(false); }
  };

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    const code = otp.join("");
    if (code.length !== 6) { toast.error("Enter the full 6-digit code"); return; }
    setLoading(true);
    try {
      const { data } = await authApi.verifyOtp({ email: pendingEmail || form.email, otp: code });
      setAuth(data.token, data.user);
      navigate("/welcome");
    } catch (e: any) {
      toast.error(e?.response?.data?.message ?? "Invalid OTP");
    } finally { setLoading(false); }
  };

  const handleResend = async () => {
    if (cooldown > 0) return;
    try {
      await authApi.resendOtp({ email: pendingEmail || form.email });
      startCooldown();
      toast.success("OTP resent");
    } catch (e: any) {
      toast.error(e?.response?.data?.message ?? "Failed to resend");
    }
  };

  const handleForgot = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.email.trim()) { setFieldErrors({ email: "Email is required" }); return; }
    setLoading(true);
    try {
      await authApi.forgotPassword({ email: form.email });
      toast.success("Password reset link sent to your email");
      setStep("login");
    } catch (e: any) {
      toast.error(e?.response?.data?.message ?? "Failed to send reset email");
    } finally { setLoading(false); }
  };

  const onOtpChange = (i: number, v: string) => {
    if (!/^\d?$/.test(v)) return;
    const arr = [...otp]; arr[i] = v; setOtp(arr);
    if (v && i < 5) (document.getElementById(`otp-${i + 1}`) as HTMLInputElement)?.focus();
  };

  const onOtpKeyDown = (i: number, e: React.KeyboardEvent) => {
    if (e.key === "Backspace" && !otp[i] && i > 0)
      (document.getElementById(`otp-${i - 1}`) as HTMLInputElement)?.focus();
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 bg-background animate-fade-in">
      <div className="mb-8"><Logo /></div>
      <div className="card-surface w-full max-w-[440px] p-8">

        {/* ── REGISTER ── */}
        {step === "register" && (
          <form onSubmit={handleRegister} className="space-y-4">
            <div>
              <h1 className="text-2xl font-bold">Create your account</h1>
              <p className="text-sm text-muted-foreground mt-1">Start your AI-powered job search today</p>
            </div>
            <div className="space-y-1.5">
              <Label>Full Name</Label>
              <Input required value={form.name} onChange={(e) => f("name", e.target.value)} placeholder="Priya Sharma" />
              {fieldErrors.name && <p className="text-xs text-danger">{fieldErrors.name}</p>}
            </div>
            <div className="space-y-1.5">
              <Label>Email Address</Label>
              <Input type="email" required value={form.email} onChange={(e) => f("email", e.target.value)} placeholder="priya@email.com" />
              {fieldErrors.email && <p className="text-xs text-danger">{fieldErrors.email}</p>}
            </div>
            <div className="space-y-1.5">
              <Label>Password</Label>
              <div className="relative">
                <Input type={showPwd ? "text" : "password"} required minLength={8} value={form.password} onChange={(e) => f("password", e.target.value)} />
                <button type="button" onClick={() => setShowPwd((s) => !s)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground">
                  {showPwd ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
              {fieldErrors.password && <p className="text-xs text-danger">{fieldErrors.password}</p>}
            </div>
            <div className="space-y-1.5">
              <Label>Confirm Password</Label>
              <Input type="password" required value={form.confirm} onChange={(e) => f("confirm", e.target.value)} />
              {fieldErrors.confirm && <p className="text-xs text-danger">{fieldErrors.confirm}</p>}
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
              Create Account
            </Button>
            <p className="text-sm text-center text-muted-foreground">
              Already have an account?{" "}
              <button type="button" onClick={() => setStep("login")} className="text-primary">Sign in</button>
            </p>
          </form>
        )}

        {/* ── LOGIN ── */}
        {step === "login" && (
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <h1 className="text-2xl font-bold">Welcome back</h1>
              <p className="text-sm text-muted-foreground mt-1">Sign in to your CareerCopilot account</p>
            </div>
            <div className="space-y-1.5">
              <Label>Email</Label>
              <Input type="email" required value={form.email} onChange={(e) => f("email", e.target.value)} placeholder="priya@email.com" />
              {fieldErrors.email && <p className="text-xs text-danger">{fieldErrors.email}</p>}
            </div>
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <Label>Password</Label>
                <button type="button" onClick={() => setStep("forgot")} className="text-xs text-primary">Forgot password?</button>
              </div>
              <Input type="password" required value={form.password} onChange={(e) => f("password", e.target.value)} />
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
              Sign In
            </Button>
            <p className="text-sm text-center text-muted-foreground">
              New here?{" "}
              <button type="button" onClick={() => setStep("register")} className="text-primary">Create account</button>
            </p>
          </form>
        )}

        {/* ── OTP VERIFY ── */}
        {step === "verify" && (
          <form onSubmit={handleVerify} className="space-y-5 text-center">
            <div className="mx-auto h-14 w-14 rounded-full bg-primary/10 flex items-center justify-center text-primary">
              <Mail className="h-7 w-7" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Verify your email</h1>
              <p className="text-sm text-muted-foreground mt-1">
                We sent a 6-digit OTP to <span className="font-medium text-foreground">{pendingEmail}</span>
              </p>
            </div>
            <div className="flex justify-center gap-2">
              {otp.map((v, i) => (
                <input
                  key={i} id={`otp-${i}`} inputMode="numeric" maxLength={1} value={v}
                  onChange={(e) => onOtpChange(i, e.target.value)}
                  onKeyDown={(e) => onOtpKeyDown(i, e)}
                  className="h-12 w-11 rounded-md bg-input border border-border text-center font-mono text-lg focus:outline-none focus:border-primary"
                />
              ))}
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
              Verify OTP
            </Button>
            <p className="text-sm text-muted-foreground">
              Didn't receive it?{" "}
              {cooldown > 0
                ? <span>Resend in {cooldown}s</span>
                : <button type="button" onClick={handleResend} className="text-primary">Resend OTP</button>
              }
            </p>
          </form>
        )}

        {/* ── FORGOT PASSWORD ── */}
        {step === "forgot" && (
          <form onSubmit={handleForgot} className="space-y-4">
            <div>
              <h1 className="text-2xl font-bold">Reset password</h1>
              <p className="text-sm text-muted-foreground mt-1">We'll send a reset link to your email</p>
            </div>
            <div className="space-y-1.5">
              <Label>Email Address</Label>
              <Input type="email" required value={form.email} onChange={(e) => f("email", e.target.value)} />
              {fieldErrors.email && <p className="text-xs text-danger">{fieldErrors.email}</p>}
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
              Send Reset Link
            </Button>
            <p className="text-sm text-center text-muted-foreground">
              <button type="button" onClick={() => setStep("login")} className="text-primary">← Back to sign in</button>
            </p>
          </form>
        )}
      </div>
    </div>
  );
}
