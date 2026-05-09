import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/stores/authStore";
import { CheckCircle2 } from "lucide-react";

export default function Welcome() {
  const { user } = useAuthStore();
  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-background">
      <div className="card-surface w-full max-w-[480px] p-10 text-center space-y-6">
        <div className="mx-auto h-16 w-16 rounded-full bg-success/10 flex items-center justify-center">
          <CheckCircle2 className="h-9 w-9 text-success" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">Welcome to CareerCopilot, {user?.name?.split(" ")[0] ?? "there"}! 🎉</h1>
          <p className="text-sm text-muted-foreground mt-2">Your account is verified and ready.</p>
        </div>
        <div className="rounded-lg bg-primary/5 border border-primary/15 p-4 text-left">
          <p className="text-sm text-muted-foreground">
            ✉ We've sent a welcome email to <span className="font-medium text-foreground">{user?.email}</span> with tips to get started.
          </p>
        </div>
        <div className="flex flex-col gap-3">
          <Link to="/profile/setup">
            <Button className="w-full">Complete Your Profile →</Button>
          </Link>
          <Link to="/dashboard">
            <Button variant="secondary" className="w-full">Explore Dashboard</Button>
          </Link>
        </div>
        <p className="text-xs text-muted-foreground">
          A complete profile unlocks job matching, ATS generation, and shortlist predictions.
        </p>
      </div>
    </div>
  );
}
