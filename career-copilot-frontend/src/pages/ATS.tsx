import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useResumeStore } from "@/stores/resumeStore";
import { useAnalysisStore } from "@/stores/analysisStore";
import { Copy, Download, Wand2, Loader2 } from "lucide-react";
import { toast } from "sonner";

export default function ATS() {
  const { resumes, fetchResumes } = useResumeStore();
  const { atsResult, atsLoading, generateATS, error } = useAnalysisStore();
  const [form, setForm] = useState({ title: "", company: "", jd: "", resumeId: "" });

  useEffect(() => { if (resumes.length === 0) fetchResumes().catch(() => {}); }, [fetchResumes, resumes.length]);

  // Auto-select first uploaded resume
  useEffect(() => {
    if (!form.resumeId && resumes.length > 0) {
      const first = resumes.find((r) => r.type === "uploaded");
      if (first) setForm((p) => ({ ...p, resumeId: first.id }));
    }
  }, [resumes]);

  const generate = async () => {
    if (!form.resumeId) { toast.error("Select a resume first"); return; }
    if (!form.jd.trim()) { toast.error("Paste a job description"); return; }
    if (!form.title.trim()) { toast.error("Enter the job title"); return; }
    try {
      await generateATS({ resumeId: form.resumeId, title: form.title, company: form.company, jd: form.jd });
      toast.success("ATS resume generated!");
    } catch (e: any) {
      toast.error(e?.response?.data?.message ?? "Generation failed");
    }
  };

  const copyToClipboard = () => {
    if (!atsResult) return;
    navigator.clipboard.writeText(atsResult.content);
    toast.success("Copied to clipboard");
  };

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      {/* Input panel */}
      <div className="card-surface p-6 space-y-4">
        <h2 className="font-bold">Job Details</h2>
        <div>
          <Label>Target Job Title *</Label>
          <Input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="e.g. Senior Software Engineer" />
        </div>
        <div>
          <Label>Company (optional)</Label>
          <Input value={form.company} onChange={(e) => setForm({ ...form, company: e.target.value })} placeholder="e.g. Google" />
        </div>
        <div>
          <Label>Paste Job Description *</Label>
          <Textarea rows={10} value={form.jd} onChange={(e) => setForm({ ...form, jd: e.target.value })} placeholder="Paste the full job description here for best ATS optimization…" />
        </div>
        <div>
          <Label>Select Resume *</Label>
          <Select value={form.resumeId} onValueChange={(v) => setForm({ ...form, resumeId: v })}>
            <SelectTrigger>
              <SelectValue placeholder="Choose a resume…" />
            </SelectTrigger>
            <SelectContent>
              {resumes.length === 0
                ? <SelectItem value="none" disabled>No resumes uploaded yet</SelectItem>
                : resumes.map((r) => <SelectItem key={r.id} value={r.id}>{r.filename}</SelectItem>)
              }
            </SelectContent>
          </Select>
        </div>
        <Button className="w-full" onClick={generate} disabled={atsLoading}>
          {atsLoading
            ? <><Loader2 className="h-4 w-4 animate-spin mr-2" /> Generating…</>
            : <><Wand2 className="h-4 w-4 mr-2" /> Generate ATS Resume</>
          }
        </Button>
        {error && <p className="text-xs text-danger">{error}</p>}
      </div>

      {/* Output panel */}
      <div className="card-surface p-6">
        {!atsResult ? (
          <div className="border-2 border-dashed border-border rounded-lg h-full min-h-[400px] flex items-center justify-center text-center p-8">
            <div>
              <Wand2 className="h-8 w-8 mx-auto text-muted-foreground" />
              <p className="mt-3 text-sm font-medium">ATS-optimized resume appears here</p>
              <p className="text-xs text-muted-foreground mt-1">Fill in the job details and click Generate</p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {/* ATS Score */}
            <div>
              <div className="flex items-baseline justify-between">
                <span className="text-sm text-muted-foreground">ATS Score</span>
                <span className={`font-mono text-2xl font-bold ${atsResult.atsScore >= 80 ? "text-success" : atsResult.atsScore >= 60 ? "text-warning" : "text-danger"}`}>
                  {atsResult.atsScore}
                </span>
              </div>
              <div className="h-2 bg-secondary rounded-full mt-2 overflow-hidden">
                <div className={`h-full rounded-full ${atsResult.atsScore >= 80 ? "bg-success" : atsResult.atsScore >= 60 ? "bg-warning" : "bg-danger"}`}
                  style={{ width: `${atsResult.atsScore}%` }} />
              </div>
            </div>

            {/* Keywords */}
            <div>
              <p className="text-sm font-semibold mb-2">Keyword Match</p>
              <div className="flex flex-wrap gap-1.5">
                {atsResult.matchedKeywords.map((k) => <span key={k} className="pill bg-success/15 text-success text-xs">{k}</span>)}
                {atsResult.missingKeywords.map((k) => <span key={k} className="pill bg-danger/15 text-danger text-xs">{k}</span>)}
              </div>
            </div>

            {/* Resume preview */}
            <pre className="font-mono text-xs bg-background border border-border rounded-md p-4 overflow-auto max-h-[500px] leading-relaxed whitespace-pre-wrap">
              {atsResult.content}
            </pre>

            {/* Actions */}
            <div className="flex gap-2">
              <Button variant="secondary" className="flex-1" onClick={copyToClipboard}>
                <Copy className="h-4 w-4 mr-2" /> Copy
              </Button>
              <Button className="flex-1" onClick={() => toast.info("PDF download coming soon")}>
                <Download className="h-4 w-4 mr-2" /> Download PDF
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
