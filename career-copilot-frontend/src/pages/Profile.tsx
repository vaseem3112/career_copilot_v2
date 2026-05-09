import { useEffect } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { useProfileStore } from "@/stores/profileStore";
import { ArrowRight, User, MapPin, Mail, Phone, Linkedin, Github } from "lucide-react";

export default function Profile() {
  const { profile, completionScore, loading, fetchProfile, fetchCompletion } = useProfileStore();

  useEffect(() => {
    fetchProfile();
    fetchCompletion();
  }, []);

  if (loading) return (
    <div className="max-w-3xl mx-auto space-y-4">
      <Skeleton className="h-32 w-full rounded-xl" />
      <Skeleton className="h-48 w-full rounded-xl" />
    </div>
  );

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header card */}
      <div className="card-surface p-6 flex flex-col sm:flex-row gap-5 items-start sm:items-center">
        <div className="h-16 w-16 rounded-full bg-primary/20 flex items-center justify-center text-2xl font-bold text-primary shrink-0">
          {profile?.name?.[0]?.toUpperCase() ?? <User className="h-8 w-8" />}
        </div>
        <div className="flex-1">
          <h2 className="text-xl font-bold">{profile?.name ?? "—"}</h2>
          <div className="flex flex-wrap gap-x-4 gap-y-1 mt-2 text-sm text-muted-foreground">
            {profile?.email    && <span className="flex items-center gap-1"><Mail      className="h-3 w-3" />{profile.email}</span>}
            {profile?.phone    && <span className="flex items-center gap-1"><Phone     className="h-3 w-3" />{profile.phone}</span>}
            {profile?.city     && <span className="flex items-center gap-1"><MapPin    className="h-3 w-3" />{profile.city}{profile.country ? `, ${profile.country}` : ""}</span>}
            {profile?.linkedin && <a href={profile.linkedin} target="_blank" rel="noreferrer" className="flex items-center gap-1 hover:text-primary"><Linkedin className="h-3 w-3" />LinkedIn</a>}
            {profile?.github   && <a href={profile.github}   target="_blank" rel="noreferrer" className="flex items-center gap-1 hover:text-primary"><Github   className="h-3 w-3" />GitHub</a>}
          </div>
        </div>
        <Link to="/profile/setup">
          <Button variant="secondary" size="sm">Edit Profile <ArrowRight className="h-3.5 w-3.5 ml-2" /></Button>
        </Link>
      </div>

      {/* Completion */}
      <div className="card-surface p-5">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-sm">Profile Completeness</h3>
          <span className="font-mono text-sm font-bold text-primary">{completionScore}%</span>
        </div>
        <Progress value={completionScore} className="h-2" />
        {completionScore < 100 && (
          <p className="text-xs text-muted-foreground mt-2">
            Complete your profile to unlock all AI features.{" "}
            <Link to="/profile/setup" className="text-primary hover:underline">Continue setup →</Link>
          </p>
        )}
      </div>

      {/* Summary */}
      {profile?.summary && (
        <div className="card-surface p-5">
          <h3 className="font-semibold mb-2">Summary</h3>
          <p className="text-sm text-muted-foreground leading-relaxed">{profile.summary}</p>
        </div>
      )}

      {/* Skills */}
      {(profile?.skills ?? []).length > 0 && (
        <div className="card-surface p-5">
          <h3 className="font-semibold mb-3">Skills</h3>
          <div className="flex flex-wrap gap-2">
            {profile!.skills!.map((s, i) => (
              <span key={i} className="pill bg-primary/10 text-primary border border-primary/20">{s}</span>
            ))}
          </div>
        </div>
      )}

      {/* Experience */}
      {(profile?.experience ?? []).length > 0 && (
        <div className="card-surface p-5 space-y-4">
          <h3 className="font-semibold">Work Experience</h3>
          {profile!.experience!.map((e: any, i: number) => (
            <div key={i} className={i > 0 ? "pt-4 border-t border-border" : ""}>
              <div className="flex justify-between items-start flex-wrap gap-1">
                <div>
                  <p className="font-medium text-sm">{e.title}</p>
                  <p className="text-xs text-muted-foreground">{e.company}</p>
                </div>
                <p className="text-xs text-muted-foreground">
                  {e.start} — {e.current ? "Present" : e.end}
                </p>
              </div>
              {e.description && <p className="text-sm text-muted-foreground mt-1.5">{e.description}</p>}
            </div>
          ))}
        </div>
      )}

      {/* Education */}
      {(profile?.education ?? []).length > 0 && (
        <div className="card-surface p-5 space-y-4">
          <h3 className="font-semibold">Education</h3>
          {profile!.education!.map((e: any, i: number) => (
            <div key={i} className={i > 0 ? "pt-4 border-t border-border" : ""}>
              <div className="flex justify-between items-start flex-wrap gap-1">
                <div>
                  <p className="font-medium text-sm">{e.degree} {e.field ? `in ${e.field}` : ""}</p>
                  <p className="text-xs text-muted-foreground">{e.institution}</p>
                </div>
                <p className="text-xs text-muted-foreground">{e.startYear} — {e.endYear}</p>
              </div>
              {e.grade && <p className="text-xs text-muted-foreground mt-1">Grade: {e.grade}</p>}
            </div>
          ))}
        </div>
      )}

      {/* Certifications */}
      {(profile?.certifications ?? []).length > 0 && (
        <div className="card-surface p-5">
          <h3 className="font-semibold mb-3">Certifications</h3>
          <div className="space-y-2">
            {profile!.certifications!.map((c: any, i: number) => (
              <div key={i} className="flex items-center justify-between text-sm">
                <span className="font-medium">{c.name}</span>
                <span className="text-xs text-muted-foreground">{c.issuer} · {c.year}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty state */}
      {!profile?.skills?.length && !profile?.experience?.length && !profile?.education?.length && (
        <div className="card-surface p-10 text-center">
          <p className="text-muted-foreground text-sm mb-4">Your profile is empty. Set it up to unlock AI features.</p>
          <Link to="/profile/setup"><Button>Set Up Profile →</Button></Link>
        </div>
      )}
    </div>
  );
}
