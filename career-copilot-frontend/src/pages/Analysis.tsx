import { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Copy, ArrowRight, AlertCircle, RefreshCw } from "lucide-react";
import { toast } from "sonner";
import { useAnalysisStore } from "@/stores/analysisStore";
import { useResumeStore } from "@/stores/resumeStore";

export default function Analysis() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const resumeId = params.get("resumeId");
  const { result, loading, error, fetchAnalysis } = useAnalysisStore();
  const { resumes } = useResumeStore();

  useEffect(() => {
    if (resumeId) {
      fetchAnalysis(resumeId);
    } else {
      // Use the first uploaded resume if no ID in URL
      const first = resumes.find((r) => r.type === "uploaded");
      if (first) fetchAnalysis(first.id);
    }
  }, [resumeId]);

  if (loading) return (
    <div className="space-y-4 max-w-4xl mx-auto">
      {["Extracting skills…", "Analyzing experience…", "Matching domains…", "Calculating shortlist probability…"].map((msg, i) => (
        <div key={i} className="card-surface p-6">
          <div className="flex items-center gap-3">
            <div className="h-2 w-2 rounded-full bg-primary animate-pulse" />
            <p className="text-sm text-muted-foreground">{msg}</p>
          </div>
          <Skeleton className="h-16 w-full mt-4" />
        </div>
      ))}
    </div>
  );

  if (error || !result) return (
    <div className="max-w-md mx-auto card-surface p-8 text-center space-y-3">
      <AlertCircle className="h-8 w-8 mx-auto text-danger" />
      <h2 className="font-bold">Couldn't load analysis</h2>
      <p className="text-sm text-muted-foreground">{error ?? "No analysis available. Upload and analyze a resume first."}</p>
      <div className="flex gap-2 justify-center">
        <Button onClick={() => resumeId && fetchAnalysis(resumeId)}><RefreshCw className="h-4 w-4 mr-2" />Retry</Button>
        <Button variant="secondary" onClick={() => navigate("/resume")}>Upload Resume</Button>
      </div>
    </div>
  );

  const prob = result.shortlistProbability;
  const probColor = prob >= 70 ? "text-success" : prob >= 40 ? "text-warning" : "text-danger";
  const strokeColor = prob >= 70 ? "hsl(var(--success))" : prob >= 40 ? "hsl(var(--warning))" : "hsl(var(--danger))";

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Banner */}
      <div className="card-surface p-6 flex flex-col md:flex-row gap-6 items-center">
        <div className="relative h-[100px] w-[100px] shrink-0">
          <svg viewBox="0 0 100 100" className="h-full w-full -rotate-90">
            <circle cx="50" cy="50" r="42" fill="none" stroke="hsl(var(--secondary))" strokeWidth="8" />
            <circle cx="50" cy="50" r="42" fill="none" stroke={strokeColor} strokeWidth="8"
              strokeDasharray={`${(prob / 100) * 264} 264`} strokeLinecap="round"
              style={{ transition: "stroke-dasharray 1s ease" }} />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={`font-mono text-2xl font-bold ${probColor}`}>{prob}%</span>
            <span className="text-[10px] text-muted-foreground">shortlist</span>
          </div>
        </div>
        <div className="flex-1">
          <h2 className="font-bold">Profile Summary</h2>
          <p className="text-sm text-muted-foreground mt-1">{result.summary}</p>
          <div className="flex flex-wrap gap-2 mt-3">
            {result.tags.map((t, i) => (
              <span key={t} className={`pill ${i === 0 ? "bg-primary/15 text-primary" : "bg-secondary text-foreground"}`}>{t}</span>
            ))}
          </div>
        </div>
      </div>

      {/* Detected Skills */}
      {result.detectedSkills.length > 0 && (
        <div className="card-surface p-6">
          <h2 className="font-bold">Detected Skills</h2>
          <div className="flex flex-wrap gap-2 mt-4">
            {result.detectedSkills.map((s) => (
              <span key={s} className="pill bg-primary/10 text-primary border border-primary/20">{s}</span>
            ))}
          </div>
        </div>
      )}

      {/* Suggested Roles */}
      {result.suggestedRoles.length > 0 && (
        <div className="card-surface p-6">
          <h2 className="font-bold">Suggested Roles</h2>
          <div className="grid sm:grid-cols-2 gap-3 mt-4">
            {result.suggestedRoles.map((x) => (
              <div key={x.name} className="rounded-lg bg-secondary/50 p-4">
                <div className="flex justify-between items-baseline">
                  <p className="font-semibold text-sm">{x.name}</p>
                  <span className="font-mono text-primary text-sm">{x.score}%</span>
                </div>
                <div className="h-1.5 bg-background rounded-full mt-2 overflow-hidden">
                  <div className="h-full bg-primary transition-all" style={{ width: `${x.score}%` }} />
                </div>
                <p className="text-xs text-muted-foreground mt-2">{x.reason}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Strengths / Weaknesses */}
      <div className="grid md:grid-cols-2 gap-4">
        <div className="card-surface p-6 border-l-4 border-l-success">
          <h3 className="font-bold">Strengths</h3>
          <ul className="mt-3 text-sm space-y-1.5 text-muted-foreground">
            {result.strengths.map((s) => <li key={s}>✓ {s}</li>)}
          </ul>
        </div>
        <div className="card-surface p-6 border-l-4 border-l-danger">
          <h3 className="font-bold">Weaknesses</h3>
          <ul className="mt-3 text-sm space-y-1.5 text-muted-foreground">
            {result.weaknesses.map((s) => <li key={s}>• {s}</li>)}
          </ul>
        </div>
      </div>

      {/* Missing skills */}
      {result.missingSkills.length > 0 && (
        <div className="card-surface p-6">
          <h3 className="font-bold">Missing Skills</h3>
          <div className="flex flex-wrap gap-2 mt-3">
            {result.missingSkills.map((s) => <span key={s} className="pill bg-warning/15 text-warning">{s}</span>)}
          </div>
        </div>
      )}

      {/* Skill Gap */}
      <div className="card-surface p-6 grid md:grid-cols-2 gap-6">
        <div>
          <h3 className="font-bold">You Have</h3>
          <div className="flex flex-wrap gap-2 mt-3">
            {result.haveSkills.map((s) => <span key={s} className="pill bg-success/15 text-success">{s}</span>)}
          </div>
        </div>
        <div>
          <h3 className="font-bold">You Need</h3>
          <div className="flex flex-wrap gap-2 mt-3">
            {result.needSkills.map((s) => <span key={s} className="pill bg-danger/15 text-danger">{s}</span>)}
          </div>
        </div>
      </div>

      {/* Improvement Plan */}
      {result.improvementPlan.length > 0 && (
        <div className="card-surface p-6 bg-primary/5 border-primary/20">
          <h3 className="font-bold">Improvement Plan</h3>
          <ol className="mt-3 text-sm space-y-2 list-decimal list-inside text-foreground/90">
            {result.improvementPlan.map((s, i) => <li key={i}>{s}</li>)}
          </ol>
        </div>
      )}

      {/* ATS Resume Preview */}
      {result.resumePreview && (
        <div className="card-surface p-6">
          <div className="flex items-center justify-between">
            <h3 className="font-bold">ATS Resume Preview</h3>
            <Button size="sm" variant="ghost" onClick={() => { navigator.clipboard.writeText(result.resumePreview); toast.success("Copied"); }}>
              <Copy className="h-3.5 w-3.5 mr-2" /> Copy
            </Button>
          </div>
          <pre className="mt-3 font-mono text-xs bg-background border border-border rounded-md p-4 overflow-auto max-h-72 leading-relaxed whitespace-pre-wrap">
            {result.resumePreview}
          </pre>
        </div>
      )}

      <Button onClick={() => navigate("/ats")}>
        Analyze against a specific job <ArrowRight className="ml-2 h-4 w-4" />
      </Button>
    </div>
  );
}
