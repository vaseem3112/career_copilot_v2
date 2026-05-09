import { Link } from "react-router-dom";

export function Logo({ className = "" }: { className?: string }) {
  return (
    <Link to="/" className={`inline-flex items-center gap-2 ${className}`}>
      <span className="text-lg font-extrabold tracking-tight text-foreground">
        CareerCopilot
      </span>
      <span className="h-2 w-2 rounded-full bg-primary" />
    </Link>
  );
}
