import { NavLink, useLocation, useNavigate, Outlet } from "react-router-dom";
import {
  Home, User, FileText, Target, Wand2, BarChart3,
  Settings as SettingsIcon, Bell, ChevronDown, LogOut, Menu, X,
} from "lucide-react";
import { Logo } from "@/components/Logo";
import { useAuthStore } from "@/stores/authStore";
import { useUIStore } from "@/stores/uiStore";
import { useProfileStore } from "@/stores/profileStore";
import { notificationsApi } from "@/lib/api";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem,
  DropdownMenuTrigger, DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import { Sheet, SheetContent } from "@/components/ui/sheet";
import { useEffect, useState } from "react";
import { useIsMobile } from "@/hooks/use-mobile";
import { toast } from "sonner";

const nav = [
  { to: "/dashboard", label: "Dashboard",   icon: Home         },
  { to: "/profile",   label: "My Profile",  icon: User         },
  { to: "/resume",    label: "Resume",       icon: FileText     },
  { to: "/jobs",      label: "Job Matches",  icon: Target       },
  { to: "/ats",       label: "ATS Builder",  icon: Wand2        },
  { to: "/analysis",  label: "Analysis",     icon: BarChart3    },
  { to: "/settings",  label: "Settings",     icon: SettingsIcon },
];

const titles: Record<string, string> = {
  "/dashboard": "Dashboard",  "/profile":  "My Profile",
  "/resume":    "Resume",     "/jobs":     "Job Matches",
  "/ats":       "ATS Builder","/analysis": "Analysis",
  "/settings":  "Settings",
};

interface Notification { id: string; message: string; read: boolean; created_at: string; }

export default function AppLayout() {
  const { user, logout }          = useAuthStore();
  const { sidebarOpen, toggleSidebar } = useUIStore();
  const { fetchProfile, fetchCompletion } = useProfileStore();
  const { pathname }              = useLocation();
  const navigate                  = useNavigate();
  const isMobile                  = useIsMobile();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [notifOpen, setNotifOpen] = useState(false);
  const title = titles[pathname] || "CareerCopilot";
  const unread = notifications.filter((n) => !n.read).length;

  // Fetch profile + notifications on mount
  useEffect(() => {
    fetchProfile().catch(() => {});
    fetchCompletion().catch(() => {});
    notificationsApi.list()
      .then(({ data }) => setNotifications(data.notifications ?? data))
      .catch(() => {});
  }, []);

  useEffect(() => { setMobileOpen(false); }, [pathname]);

  const markAllRead = async () => {
    try {
      await notificationsApi.readAll();
      setNotifications((p) => p.map((n) => ({ ...n, read: true })));
    } catch { toast.error("Failed to mark as read"); }
  };

  const handleLogout = async () => {
    try { await notificationsApi.list(); } catch (_) {} // flush
    logout();
    navigate("/");
    toast.success("Signed out");
  };

  const SidebarInner = (
    <>
      <div className="h-16 flex items-center px-4 border-b border-sidebar-border justify-between">
        {(sidebarOpen || isMobile) ? <Logo /> : <span className="h-2.5 w-2.5 rounded-full bg-primary mx-auto" />}
        {isMobile && (
          <button onClick={() => setMobileOpen(false)} className="text-muted-foreground hover:text-foreground ml-auto">
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      <nav className="flex-1 p-2 space-y-0.5 overflow-y-auto">
        {nav.map((item) => (
          <NavLink
            key={item.to} to={item.to} end
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors ${
                isActive
                  ? "bg-primary/10 text-primary font-medium"
                  : "text-muted-foreground hover:bg-sidebar-accent hover:text-foreground"
              }`
            }
          >
            <item.icon className="h-4 w-4 shrink-0" />
            {(sidebarOpen || isMobile) && <span>{item.label}</span>}
          </NavLink>
        ))}
      </nav>

      <div className="p-3 border-t border-sidebar-border">
        {(sidebarOpen || isMobile) ? (
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-full bg-primary/20 flex items-center justify-center text-sm font-semibold text-primary shrink-0">
              {user?.name?.[0]?.toUpperCase() || "U"}
            </div>
            <div className="min-w-0">
              <p className="text-sm font-medium truncate">{user?.name}</p>
              <span className="pill bg-secondary text-[10px] text-muted-foreground">Free Plan</span>
            </div>
          </div>
        ) : (
          <div className="h-9 w-9 mx-auto rounded-full bg-primary/20 flex items-center justify-center text-sm font-semibold text-primary">
            {user?.name?.[0]?.toUpperCase() || "U"}
          </div>
        )}
      </div>
    </>
  );

  return (
    <div className="min-h-screen flex bg-background text-foreground">
      {/* Desktop sidebar */}
      <aside className={`${sidebarOpen ? "w-60" : "w-16"} hidden md:flex flex-col bg-sidebar border-r border-sidebar-border transition-all duration-200`}>
        {SidebarInner}
      </aside>

      {/* Mobile sidebar */}
      <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
        <SheetContent side="left" className="p-0 w-60 bg-sidebar border-sidebar-border flex flex-col">
          {SidebarInner}
        </SheetContent>
      </Sheet>

      <div className="flex-1 flex flex-col min-w-0">
        {/* Top navbar */}
        <header className="h-16 sticky top-0 z-30 bg-background/80 backdrop-blur border-b border-border flex items-center justify-between px-4 md:px-6">
          <div className="flex items-center gap-3">
            <button
              onClick={() => isMobile ? setMobileOpen(true) : toggleSidebar()}
              className="text-muted-foreground hover:text-foreground"
              aria-label="Toggle menu"
            >
              <Menu className="h-5 w-5" />
            </button>
            <h1 className="text-lg font-bold">{title}</h1>
          </div>

          <div className="flex items-center gap-2">
            {/* Notification bell */}
            <div className="relative">
              <button
                onClick={() => setNotifOpen((p) => !p)}
                className="relative h-9 w-9 rounded-md hover:bg-secondary flex items-center justify-center text-muted-foreground"
              >
                <Bell className="h-4 w-4" />
                {unread > 0 && (
                  <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-primary" />
                )}
              </button>

              {notifOpen && (
                <div className="absolute right-0 top-11 w-80 bg-background border border-border rounded-lg shadow-lg z-50 overflow-hidden">
                  <div className="flex items-center justify-between px-4 py-3 border-b border-border">
                    <p className="text-sm font-semibold">Notifications</p>
                    {unread > 0 && (
                      <button onClick={markAllRead} className="text-xs text-primary hover:underline">
                        Mark all as read
                      </button>
                    )}
                  </div>
                  <div className="max-h-72 overflow-y-auto divide-y divide-border">
                    {notifications.length === 0
                      ? <p className="text-sm text-muted-foreground text-center py-8">You're all caught up</p>
                      : notifications.slice(0, 10).map((n) => (
                          <div key={n.id} className={`px-4 py-3 text-sm ${n.read ? "text-muted-foreground" : "text-foreground font-medium"}`}>
                            <p>{n.message}</p>
                            <p className="text-xs text-muted-foreground mt-0.5">{n.created_at}</p>
                          </div>
                        ))
                    }
                  </div>
                </div>
              )}
            </div>

            {/* Avatar dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger className="flex items-center gap-2 rounded-md hover:bg-secondary px-2 py-1.5">
                <div className="h-7 w-7 rounded-full bg-primary/20 flex items-center justify-center text-xs font-semibold text-primary">
                  {user?.name?.[0]?.toUpperCase() || "U"}
                </div>
                <ChevronDown className="h-4 w-4 text-muted-foreground" />
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                <DropdownMenuItem onClick={() => navigate("/profile")}>Profile</DropdownMenuItem>
                <DropdownMenuItem onClick={() => navigate("/settings")}>Settings</DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout}>
                  <LogOut className="h-4 w-4 mr-2" /> Sign Out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-4 md:p-6 animate-fade-in">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
