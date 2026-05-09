import { Link, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Logo } from "@/components/Logo";
import {
  ScanLine, Wand2, Target, BarChart3, PercentCircle, IdCard,
  ArrowRight, CheckCircle2,
} from "lucide-react";

const features = [
  { icon: ScanLine, title: "Deep Resume Analysis", badge: "Free", desc: "Upload your resume and get instant AI feedback on structure, keywords, clarity and domain alignment." },
  { icon: Wand2, title: "ATS-Optimized Resume", badge: "AI Powered", desc: "Paste any job description and we rewrite your resume to match it — using only your real experience, nothing fabricated." },
  { icon: Target, title: "Smart Job Matching", badge: "Live Data", desc: "We fetch live jobs from top platforms and rank them by how well your profile matches — with real similarity scores." },
  { icon: BarChart3, title: "Know Your Skill Gaps", badge: "Personalized", desc: "See exactly which skills you have vs what jobs require. Get a personalized upskilling roadmap." },
  { icon: PercentCircle, title: "Shortlist Predictor", badge: "ML Model", desc: "Our ML model calculates your real shortlist probability based on skills match, experience, and resume quality." },
  { icon: IdCard, title: "Smart Profile Builder", badge: "Auto-fill", desc: "Build a structured career profile from your resume automatically. One profile, used across all features." },
];

const testimonials = [
  { name: "Priya S.", role: "Product Manager", quote: "Finally, an AI tool that doesn't fabricate experience. My ATS score went from 42 to 87.", color: "bg-primary/20 text-primary" },
  { name: "Marcus T.", role: "Software Engineer", quote: "The skill gap analysis pointed me to exactly what to learn. Got 3 interviews in two weeks.", color: "bg-success/20 text-success" },
  { name: "Aisha K.", role: "Data Analyst", quote: "Shortlist predictor is scary accurate. Stopped wasting time on jobs I had no shot at.", color: "bg-warning/20 text-warning" },
];

export default function Landing() {
  const [scrolled, setScrolled] = useState(false);
  const navigate = useNavigate();
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className={`sticky top-0 z-50 backdrop-blur-md bg-background/70 ${scrolled ? "border-b border-border" : ""}`}>
        <div className="container mx-auto flex h-16 items-center justify-between">
          <Logo />
          <nav className="flex items-center gap-2">
            <Button variant="ghost" onClick={() => navigate("/auth")}>Sign In</Button>
            <Button onClick={() => navigate("/auth?mode=register")}>Get Started</Button>
          </nav>
        </div>
      </header>

      <section className="container mx-auto px-4 pt-20 pb-24 text-center animate-fade-in">
        <span className="pill bg-primary/10 text-primary border border-primary/20">AI-Powered Career Platform</span>
        <h1 className="mt-6 text-4xl md:text-6xl font-extrabold tracking-tight leading-[1.05]">
          Land Your Dream Job
          <br />
          <span className="text-muted-foreground font-bold">With AI That Actually Works</span>
        </h1>
        <p className="mt-6 max-w-2xl mx-auto text-muted-foreground text-lg">
          CareerCopilot analyzes your resume, matches real jobs, generates ATS-optimized applications and predicts your shortlist chances — all in one place.
        </p>
        <div className="mt-8 flex flex-wrap justify-center gap-3">
          <Button size="lg" onClick={() => navigate("/auth?mode=register")}>Create Free Account</Button>
          <Button size="lg" variant="ghost">See How It Works</Button>
        </div>
        <p className="mt-5 text-sm text-muted-foreground">No credit card · Free forever · 10,000+ users</p>
      </section>

      <section className="container mx-auto px-4 py-16">
        <h2 className="text-3xl md:text-4xl font-extrabold text-center">Everything you need to get hired faster</h2>
        <div className="mt-12 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {features.map((f) => (
            <div key={f.title} className="card-surface p-6 hover:bg-card-hover group">
              <div className="flex items-start justify-between">
                <div className="rounded-lg bg-primary/10 p-2.5 text-primary"><f.icon className="h-5 w-5" /></div>
                <span className="pill bg-secondary text-muted-foreground text-[10px] uppercase tracking-wide">{f.badge}</span>
              </div>
              <h3 className="mt-4 text-lg font-bold">{f.title}</h3>
              <p className="mt-2 text-sm text-muted-foreground leading-relaxed">{f.desc}</p>
              <Link to="/auth" className="mt-5 inline-flex items-center gap-1 text-sm text-primary group-hover:gap-2">
                Unlock this <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </div>
          ))}
        </div>
      </section>

      <section className="container mx-auto px-4 py-20">
        <h2 className="text-3xl md:text-4xl font-extrabold text-center">How CareerCopilot works</h2>
        <div className="mt-14 relative grid gap-8 md:grid-cols-3 max-w-4xl mx-auto">
          <div className="hidden md:block absolute top-6 left-[16%] right-[16%] h-px bg-border" />
          {["Create Account & Verify Email", "Upload Resume or Build Profile", "Get AI Analysis, Matches & Apply"].map((step, i) => (
            <div key={step} className="relative text-center">
              <div className="mx-auto h-12 w-12 rounded-full bg-card border border-border flex items-center justify-center font-mono font-bold text-primary relative z-10">
                {i + 1}
              </div>
              <p className="mt-4 font-semibold">{step}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="container mx-auto px-4 py-20">
        <h2 className="text-3xl md:text-4xl font-extrabold text-center">Trusted by job seekers</h2>
        <div className="mt-12 grid gap-5 md:grid-cols-3">
          {testimonials.map((t) => (
            <div key={t.name} className="card-surface p-6">
              <p className="text-sm leading-relaxed">"{t.quote}"</p>
              <div className="mt-5 flex items-center gap-3">
                <div className={`h-10 w-10 rounded-full flex items-center justify-center font-bold ${t.color}`}>{t.name[0]}</div>
                <div>
                  <p className="text-sm font-semibold">{t.name}</p>
                  <p className="text-xs text-muted-foreground">{t.role}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      <footer className="border-t border-border mt-20">
        <div className="container mx-auto px-4 py-10 flex flex-col md:flex-row items-center justify-between gap-4">
          <Logo />
          <div className="flex gap-6 text-sm text-muted-foreground">
            <a href="#">Privacy</a><a href="#">Terms</a><a href="#">Contact</a>
          </div>
          <p className="text-xs text-muted-foreground">© 2026 CareerCopilot</p>
        </div>
      </footer>
    </div>
  );
}
