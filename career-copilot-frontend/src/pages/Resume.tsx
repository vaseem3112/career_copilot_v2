import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { useResumeStore } from "@/stores/resumeStore";
import { Upload, FileText, Trash2, BarChart3, ArrowRight, Loader2 } from "lucide-react";
import { toast } from "sonner";

export default function Resume() {
  const { resumes, fetchResumes, uploadResume, deleteResume, analyzeResume, uploading, uploadProgress, loading } = useResumeStore();
  const navigate = useNavigate();

  useEffect(() => {
    fetchResumes().catch((e) => toast.error(e?.response?.data?.message ?? "Failed to load resumes"));
  }, [fetchResumes]);

  const handleFiles = async (files: FileList | null) => {
    if (!files?.[0]) return;
    const f = files[0];
    if (f.size > 5 * 1024 * 1024) { toast.error("Max 5MB"); return; }
    const allowed = ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"];
    if (!allowed.includes(f.type)) { toast.error("Only PDF, DOC, DOCX allowed"); return; }
    try {
      const resume = await uploadResume(f);
      toast.success("Resume uploaded! Starting analysis…");
      // Auto-trigger analysis after upload
      try {
        await analyzeResume(resume.id);
        toast.success("Analysis complete");
      } catch (_) { /* analysis runs async on backend */ }
    } catch (e: any) {
      toast.error(e?.response?.data?.message ?? "Upload failed");
    }
  };

  const handleDelete = async (id: string) => {
    try { await deleteResume(id); toast.success("Deleted"); }
    catch (e: any) { toast.error(e?.response?.data?.message ?? "Delete failed"); }
  };

  const handleAnalyze = async (id: string) => {
    try {
      await analyzeResume(id);
      navigate(`/analysis?resumeId=${id}`);
    } catch (e: any) {
      // Analysis may already be running or complete — navigate anyway
      navigate(`/analysis?resumeId=${id}`);
    }
  };

  const scoreColor = (s: number) =>
    s >= 80 ? "bg-success/15 text-success" : s >= 60 ? "bg-warning/15 text-warning" : "bg-danger/15 text-danger";

  const uploaded  = resumes.filter((r) => r.type === "uploaded");
  const generated = resumes.filter((r) => r.type === "generated");

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      {/* Upload panel */}
      <div className="card-surface p-6">
        <h2 className="font-bold mb-4">Upload Resume</h2>
        <label
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => { e.preventDefault(); handleFiles(e.dataTransfer.files); }}
          className="block border-2 border-dashed border-border rounded-lg p-10 text-center cursor-pointer hover:border-primary hover:bg-card-hover transition-colors"
        >
          {uploading
            ? <Loader2 className="h-8 w-8 mx-auto text-primary animate-spin" />
            : <Upload className="h-8 w-8 mx-auto text-muted-foreground" />
          }
          <p className="mt-3 font-medium">{uploading ? "Uploading…" : "Drag & drop your resume here"}</p>
          <p className="text-xs text-muted-foreground mt-1">Supports PDF, DOC, DOCX · Max 5MB</p>
          <Button variant="secondary" size="sm" className="mt-4" type="button" disabled={uploading}>Browse Files</Button>
          <input type="file" accept=".pdf,.doc,.docx" hidden onChange={(e) => handleFiles(e.target.files)} disabled={uploading} />
        </label>
        {uploading && (
          <div className="mt-4">
            <Progress value={uploadProgress} className="h-1.5" />
            <p className="text-xs text-muted-foreground mt-2">Uploading… {uploadProgress}%</p>
          </div>
        )}
      </div>

      {/* Resume list panel */}
      <div className="card-surface p-6">
        <Tabs defaultValue="uploaded">
          <TabsList>
            <TabsTrigger value="uploaded">Uploaded ({uploaded.length})</TabsTrigger>
            <TabsTrigger value="generated">AI Generated ({generated.length})</TabsTrigger>
          </TabsList>

          <TabsContent value="uploaded" className="mt-4 space-y-3">
            {loading
              ? Array.from({ length: 2 }).map((_, i) => <Skeleton key={i} className="h-16 w-full rounded-lg" />)
              : uploaded.length === 0
                ? <p className="text-sm text-muted-foreground py-8 text-center">No resumes yet. Upload one to get started.</p>
                : uploaded.map((r) => (
                    <div key={r.id} className="flex items-center gap-3 rounded-lg bg-secondary/60 p-3">
                      <div className="rounded-md bg-primary/10 p-2 text-primary shrink-0"><FileText className="h-4 w-4" /></div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{r.filename}</p>
                        <p className="text-xs text-muted-foreground">{new Date(r.uploadedAt).toLocaleDateString()}</p>
                        {r.status && <p className="text-xs text-muted-foreground capitalize">{r.status}</p>}
                      </div>
                      {r.atsScore != null && <span className={`pill ${scoreColor(r.atsScore)} font-mono shrink-0`}>{r.atsScore}</span>}
                      <div className="flex gap-1 shrink-0">
                        <Button size="icon" variant="ghost" title="Analyze" onClick={() => handleAnalyze(r.id)}><BarChart3 className="h-4 w-4" /></Button>
                        <Button size="icon" variant="ghost" title="Delete" onClick={() => handleDelete(r.id)}><Trash2 className="h-4 w-4" /></Button>
                      </div>
                    </div>
                  ))
            }
          </TabsContent>

          <TabsContent value="generated" className="mt-4 space-y-3">
            {generated.length === 0
              ? <p className="text-sm text-muted-foreground py-8 text-center">No AI-generated resumes yet.</p>
              : generated.map((r) => (
                  <div key={r.id} className="flex items-center gap-3 rounded-lg bg-secondary/60 p-3">
                    <div className="rounded-md bg-primary/10 p-2 text-primary shrink-0"><FileText className="h-4 w-4" /></div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{r.filename}</p>
                      <p className="text-xs text-muted-foreground">{new Date(r.uploadedAt).toLocaleDateString()}</p>
                    </div>
                    {r.atsScore != null && <span className={`pill ${scoreColor(r.atsScore)} font-mono shrink-0`}>{r.atsScore}</span>}
                  </div>
                ))
            }
          </TabsContent>
        </Tabs>
      </div>

      <div className="lg:col-span-2">
        <Button className="w-full" onClick={() => navigate("/ats")}>
          Generate ATS Resume for a Job <ArrowRight className="ml-2 h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
