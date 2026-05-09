import { useEffect } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { useProfileStore } from "@/stores/profileStore";
import { useDashboardStore } from "@/stores/dashboardStore";
import { FileText, Target, Wand2, Upload, ArrowRight, Sparkles } from "lucide-react";

export default function Dashboard() {
  const { completionScore, fetchCompletion } = useProfileStore();
  const { stats, loading, fetchStats } = useDashboardStore();

  useEffect(() => {
    fetchStats();
    fetchCompletion();
  }, [fetchStats, fetchCompletion]);

  const statCards = [
    { label: "Profile Score",      value: stats?.profileScore    ?? 0,  suffix: "/100", icon: Sparkles },
    { label: "ATS Score",          value: stats?.atsScore        ?? 0,  suffix: "/100", icon: FileText },
    { label: "Job Matches Found",  value: stats?.jobMatches      ?? 0,  suffix: "",     icon: Target   },
    { label: "Shortlist Chance",   value: stats?.shortlistChance ?? 0,  suffix: "%",    icon: Wand2    },
  ];

  return (
    <div className="space-y-6">
      {/* Incomplete profile banner */}
      {completionScore < 80 && (
        <div className="card-surface p-4 md:p-5 border-warning/30 bg-warning/5 flex flex-col md:flex-row md:items-center gap-4">
          <div className="flex-1">
            <p className="text-sm font-semibold">Your profile is {completionScore}% complete.</p>
            <p className="text-xs text-muted-foreground mt-0.5">Complete it to unlock all AI features.</p>
            <Progress value={completionScore} className="mt-3 h-1.5" />
          </div>
          <Link to="/profile/setup">
            <Button>Complete Profile <ArrowRight className="ml-2 h-3.5 w-3.5" /></Button>
          </Link>
        </div>
      )}

      {/* Stat cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((s) => (
          <div key={s.label} className="card-surface p-5">
            <div className="rounded-md bg-primary/10 p-2 text-primary w-fit">
              <s.icon className="h-4 w-4" />
            </div>
            {loading
              ? <Skeleton className="h-8 w-24 mt-3" />
              : <p className="mt-3 text-3xl font-extrabold font-mono">
                  {s.value}<span className="text-base text-muted-foreground font-normal">{s.suffix}</span>
                </p>
            }
            <p className="mt-1 text-xs text-muted-foreground">{s.label}</p>
          </div>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          {/* Matched Jobs */}
          <div className="card-surface p-5">
            <div className="flex items-center justify-between">
              <h2 className="font-bold">Your Matched Jobs</h2>
              <Link to="/jobs" className="text-sm text-primary">View All Matches →</Link>
            </div>
            <div className="mt-4 divide-y divide-border">
              {loading
                ? Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-14 w-full my-2" />)
                : stats?.recentJobs?.length
                  ? stats.recentJobs.map((j) => (
                      <div key={j.title + j.company} className="flex items-center gap-4 py-3">
                        <div className="h-10 w-10 rounded-md bg-primary/15 text-primary flex items-center justify-center font-bold shrink-0">
                          {j.company?.[0] ?? "?"}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-semibold truncate">{j.title}</p>
                          <p className="text-xs text-muted-foreground">{j.company} · {j.location}</p>
                        </div>
                        <span className="pill bg-success/15 text-success shrink-0">{j.score}% match</span>
                      </div>
                    ))
                  : <p className="text-sm text-muted-foreground py-6 text-center">
                      Upload your resume to get job matches.
                    </p>
              }
            </div>
          </div>

          {/* Suggested Roles */}
          <div className="card-surface p-5">
            <h2 className="font-bold">Suggested Roles for You</h2>
            {loading
              ? <Skeleton className="h-24 w-full mt-4" />
              : <div className="mt-4 flex gap-4 overflow-x-auto pb-2">
                  {stats?.suggestedRoles?.length
                    ? stats.suggestedRoles.map((r) => (
                        <div key={r.name} className="min-w-[180px] rounded-lg bg-secondary p-4 shrink-0">
                          <p className="text-sm font-semibold">{r.name}</p>
                          <div className="mt-2 h-1.5 bg-background rounded-full overflow-hidden">
                            <div className="h-full bg-primary" style={{ width: `${r.score}%` }} />
                          </div>
                          <div className="mt-3 flex items-center justify-between text-xs">
                            <span className="font-mono text-primary">{r.score}%</span>
                            <Link to="/jobs" className="text-muted-foreground hover:text-primary">Explore →</Link>
                          </div>
                        </div>
                      ))
                    : <p className="text-sm text-muted-foreground py-4">
                        Complete your profile to see role suggestions.
                      </p>
                  }
                </div>
            }
          </div>

          {/* Quick actions */}
          <div className="grid grid-cols-3 gap-3">
            <Link to="/resume"><Button variant="secondary" className="w-full"><Upload className="h-4 w-4 mr-2" />Upload Resume</Button></Link>
            <Link to="/jobs"><Button variant="secondary" className="w-full"><Target className="h-4 w-4 mr-2" />Find Jobs</Button></Link>
            <Link to="/ats"><Button variant="secondary" className="w-full"><Wand2 className="h-4 w-4 mr-2" />Generate ATS</Button></Link>
          </div>
        </div>

        <div className="space-y-6">
          {/* Resume Health */}
          <div className="card-surface p-5">
            <h2 className="font-bold">Resume Health</h2>
            {loading
              ? <Skeleton className="h-32 w-full mt-4" />
              : stats?.resumeHealth
                ? <div className="mt-4">
                    <div className="flex items-baseline justify-between">
                      <span className="text-xs text-muted-foreground">ATS Score</span>
                      <span className="font-mono text-2xl font-bold text-success">{stats.resumeHealth.atsScore}</span>
                    </div>
                    <div className="mt-2 h-2 bg-secondary rounded-full overflow-hidden">
                      <div className="h-full bg-success" style={{ width: `${stats.resumeHealth.atsScore}%` }} />
                    </div>
                    <ul className="mt-4 space-y-2 text-sm text-muted-foreground">
                      {stats.resumeHealth.improvements.map((imp, i) => <li key={i}>• {imp}</li>)}
                    </ul>
                  </div>
                : <div className="mt-4 border-2 border-dashed border-border rounded-lg p-6 text-center">
                    <p className="text-sm text-muted-foreground">No resume uploaded yet.</p>
                    <Link to="/resume"><Button size="sm" variant="secondary" className="mt-3">Upload Resume</Button></Link>
                  </div>
            }
          </div>

          {/* Recent Activity */}
          <div className="card-surface p-5">
            <h2 className="font-bold">Recent Activity</h2>
            <ul className="mt-4 space-y-3">
              {loading
                ? Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-8 w-full" />)
                : stats?.recentActivity?.length
                  ? stats.recentActivity.map((a, i) => (
                      <li key={i} className="flex items-start gap-3 text-sm">
                        <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-primary shrink-0" />
                        <div className="flex-1">
                          <p>{a.text}</p>
                          <p className="text-xs text-muted-foreground">{a.time}</p>
                        </div>
                      </li>
                    ))
                  : <li className="text-sm text-muted-foreground">No activity yet.</li>
              }
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
