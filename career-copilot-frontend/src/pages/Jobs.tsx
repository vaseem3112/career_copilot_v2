import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Sheet, SheetContent } from "@/components/ui/sheet";
import { useJobStore, Job } from "@/stores/jobStore";
import { useAnalysisStore } from "@/stores/analysisStore";
import { useResumeStore } from "@/stores/resumeStore";
import { Bookmark, BookmarkCheck, MapPin, DollarSign, Search, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";

export default function Jobs() {
  const { jobs, matched, saved, loading, filters, tab, fetchJobs, fetchMatched, fetchSaved, saveJob, unsaveJob, setFilter, setTab } = useJobStore();
  const { resumes } = useResumeStore();
  const { generateATS } = useAnalysisStore();
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState<Job | null>(null);
  const [analyzingId, setAnalyzingId] = useState<string | null>(null);

  useEffect(() => { fetchJobs(); fetchSaved(); }, []);
  useEffect(() => { if (tab === "best") fetchMatched(); }, [tab]);

  const displayed = tab === "all" ? jobs : tab === "best" ? matched : saved;
  const filtered  = displayed.filter((j) =>
    !query || (j.title + j.company).toLowerCase().includes(query.toLowerCase())
  );

  const handleSave = async (e: React.MouseEvent, job: Job) => {
    e.stopPropagation();
    try {
      job.isSaved ? await unsaveJob(job.id) : await saveJob(job.id);
    } catch { toast.error("Failed to save job"); }
  };

  const handleAnalyzeFit = async (job: Job) => {
    const activeResume = resumes.find((r) => r.type === "uploaded");
    if (!activeResume) { toast.error("Upload a resume first"); return; }
    setAnalyzingId(job.id);
    try {
      await generateATS({
        resumeId: activeResume.id,
        title:    job.title,
        company:  job.company,
        jd:       job.description ?? "",
      });
      navigate("/ats");
    } catch { toast.error("Analysis failed"); }
    finally { setAnalyzingId(null); }
  };

  const scoreClass = (s?: number) =>
    !s ? "bg-secondary text-muted-foreground"
    : s >= 80 ? "bg-success/15 text-success"
    : s >= 60 ? "bg-warning/15 text-warning"
    : "bg-secondary text-muted-foreground";

  return (
    <div className="space-y-5">
      {/* Search + filters */}
      <div className="card-surface p-4 space-y-3">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search jobs…" className="pl-9" />
          </div>
          <Button onClick={fetchJobs} disabled={loading}>
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Search"}
          </Button>
        </div>
        <div className="flex flex-wrap gap-2">
          {["Domain", "Location", "Experience", "Job Type"].map((f) => (
            <button key={f} className="pill bg-secondary text-muted-foreground hover:text-foreground text-xs">{f}</button>
          ))}
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={tab} onValueChange={(v) => setTab(v as any)}>
        <TabsList>
          <TabsTrigger value="all">All Jobs</TabsTrigger>
          <TabsTrigger value="best">Best Matches</TabsTrigger>
          <TabsTrigger value="saved">Saved</TabsTrigger>
        </TabsList>
      </Tabs>

      {/* Job list */}
      <div className="space-y-3">
        {loading ? (
          Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-20 w-full rounded-lg" />)
        ) : filtered.length === 0 ? (
          <div className="card-surface p-12 text-center text-muted-foreground text-sm">
            {tab === "saved" ? "No saved jobs yet." : "No jobs found. Try adjusting your filters."}
          </div>
        ) : filtered.map((j) => (
          <div key={j.id} className="card-surface p-4 hover:bg-card-hover hover:-translate-y-0.5 cursor-pointer flex items-center gap-4" onClick={() => setOpen(j)}>
            <div className="h-11 w-11 rounded-md bg-primary/15 text-primary flex items-center justify-center font-bold shrink-0">
              {j.company?.[0] ?? "?"}
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-semibold truncate">{j.title}</p>
              <p className="text-xs text-muted-foreground flex items-center gap-3 mt-0.5 flex-wrap">
                <span>{j.company}</span>
                {j.location && <span className="flex items-center gap-1"><MapPin className="h-3 w-3" />{j.location}</span>}
                {j.salary  && <span className="flex items-center gap-1"><DollarSign className="h-3 w-3" />{j.salary}</span>}
                {j.posted  && <span>· {j.posted}</span>}
              </p>
            </div>
            {j.matchScore != null && (
              <span className={`pill font-mono shrink-0 ${scoreClass(j.matchScore)}`}>{j.matchScore}% match</span>
            )}
            <button onClick={(e) => handleSave(e, j)} className="text-muted-foreground hover:text-primary shrink-0">
              {j.isSaved ? <BookmarkCheck className="h-4 w-4 text-primary" /> : <Bookmark className="h-4 w-4" />}
            </button>
            <Button size="sm" variant="secondary" onClick={(e) => { e.stopPropagation(); setOpen(j); }}>View</Button>
          </div>
        ))}
      </div>

      {/* Pagination */}
      {!loading && filtered.length > 0 && (
        <div className="flex justify-center gap-1 pt-4">
          <Button variant="ghost" size="sm" disabled={filters.page <= 1} onClick={() => { setFilter("page", filters.page - 1); fetchJobs(); }}>Prev</Button>
          <Button variant="secondary" size="sm">{filters.page}</Button>
          <Button variant="ghost" size="sm" onClick={() => { setFilter("page", filters.page + 1); fetchJobs(); }}>Next</Button>
        </div>
      )}

      {/* Job detail drawer */}
      <Sheet open={!!open} onOpenChange={(v) => !v && setOpen(null)}>
        <SheetContent className="sm:max-w-lg overflow-y-auto">
          {open && (
            <div className="space-y-4 pt-4">
              <div>
                <h2 className="text-xl font-bold">{open.title}</h2>
                <p className="text-sm text-muted-foreground">{open.company} · {open.location}</p>
              </div>
              {open.matchScore != null && (
                <span className={`pill font-mono ${scoreClass(open.matchScore)}`}>{open.matchScore}% match</span>
              )}
              {open.description && (
                <div>
                  <h3 className="font-semibold text-sm">Description</h3>
                  <p className="text-sm text-muted-foreground mt-2 leading-relaxed whitespace-pre-line">{open.description}</p>
                </div>
              )}
              {open.requirements && open.requirements.length > 0 && (
                <div>
                  <h3 className="font-semibold text-sm">Requirements</h3>
                  <ul className="text-sm text-muted-foreground mt-2 space-y-1 list-disc list-inside">
                    {open.requirements.map((r, i) => <li key={i}>{r}</li>)}
                  </ul>
                </div>
              )}
              <div className="flex gap-2 pt-2">
                <Button className="flex-1" onClick={() => toast.info("Redirecting to job application…")}>Apply Now</Button>
                <Button variant="secondary" className="flex-1" disabled={analyzingId === open.id} onClick={() => handleAnalyzeFit(open)}>
                  {analyzingId === open.id ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                  Analyze My Fit
                </Button>
              </div>
            </div>
          )}
        </SheetContent>
      </Sheet>
    </div>
  );
}
