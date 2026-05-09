import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Skeleton } from "@/components/ui/skeleton";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { useAuthStore } from "@/stores/authStore";
import { settingsApi } from "@/lib/api";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";

const TABS = ["Account", "Notifications", "Privacy", "Danger Zone"];

interface NotifSettings { jobAlerts: boolean; analysisComplete: boolean; weeklyDigest: boolean; productUpdates: boolean; }
interface PrivacySettings { visibleToRecruiters: boolean; allowDataUse: boolean; }

export default function Settings() {
  const [tab, setTab]             = useState("Account");
  const [loading, setLoading]     = useState(false);
  const [saving, setSaving]       = useState(false);
  const [confirmText, setConfirmText] = useState("");
  const { user, logout }          = useAuthStore();
  const navigate                  = useNavigate();

  const [account, setAccount]   = useState({ name: user?.name ?? "", email: user?.email ?? "", phone: "" });
  const [pwd, setPwd]           = useState({ current: "", newPwd: "", confirm: "" });
  const [notifs, setNotifs]     = useState<NotifSettings>({ jobAlerts: true, analysisComplete: true, weeklyDigest: false, productUpdates: false });
  const [privacy, setPrivacy]   = useState<PrivacySettings>({ visibleToRecruiters: false, allowDataUse: true });

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const { data } = await settingsApi.get();
        const s = data.settings ?? data;
        if (s.notifications) setNotifs(s.notifications);
        if (s.privacy)       setPrivacy(s.privacy);
        if (s.phone)         setAccount((p) => ({ ...p, phone: s.phone }));
      } catch (_) {}
      finally { setLoading(false); }
    };
    load();
  }, []);

  const saveAccount = async () => {
    setSaving(true);
    try {
      await settingsApi.update({ name: account.name, email: account.email, phone: account.phone });
      toast.success("Account info saved");
    } catch (e: any) { toast.error(e?.response?.data?.message ?? "Save failed"); }
    finally { setSaving(false); }
  };

  const changePassword = async () => {
    if (pwd.newPwd !== pwd.confirm) { toast.error("Passwords don't match"); return; }
    if (pwd.newPwd.length < 8)      { toast.error("Minimum 8 characters"); return; }
    setSaving(true);
    try {
      await settingsApi.changePassword({ current_password: pwd.current, new_password: pwd.newPwd });
      setPwd({ current: "", newPwd: "", confirm: "" });
      toast.success("Password changed");
    } catch (e: any) { toast.error(e?.response?.data?.message ?? "Change failed"); }
    finally { setSaving(false); }
  };

  const saveNotifs = async (updated: NotifSettings) => {
    setNotifs(updated);
    try { await settingsApi.update({ notifications: updated }); }
    catch (_) { toast.error("Failed to save notification settings"); }
  };

  const savePrivacy = async (updated: PrivacySettings) => {
    setPrivacy(updated);
    try { await settingsApi.update({ privacy: updated }); }
    catch (_) { toast.error("Failed to save privacy settings"); }
  };

  const downloadData = async () => {
    try {
      const res = await settingsApi.downloadData();
      const url = URL.createObjectURL(res.data);
      const a   = document.createElement("a"); a.href = url; a.download = "my-careercopilot-data.json"; a.click();
      URL.revokeObjectURL(url);
    } catch (_) { toast.error("Download failed"); }
  };

  const deleteAccount = async () => {
    try {
      await settingsApi.deleteAccount();
      logout(); navigate("/"); toast.success("Account deleted");
    } catch (e: any) { toast.error(e?.response?.data?.message ?? "Delete failed"); }
  };

  return (
    <div className="grid gap-6 md:grid-cols-[200px_1fr] max-w-5xl mx-auto">
      <nav className="space-y-1">
        {TABS.map((t) => (
          <button key={t} onClick={() => setTab(t)}
            className={`block w-full text-left px-3 py-2 rounded-md text-sm ${tab === t ? "bg-primary/10 text-primary" : "text-muted-foreground hover:bg-secondary"}`}>
            {t}
          </button>
        ))}
      </nav>

      <div className="card-surface p-6">
        {loading ? <Skeleton className="h-64 w-full" /> : (
          <>
            {/* ACCOUNT */}
            {tab === "Account" && (
              <div className="space-y-4 max-w-md">
                <h2 className="font-bold">Account Information</h2>
                <div><Label>Name</Label><Input value={account.name} onChange={(e) => setAccount((p) => ({ ...p, name: e.target.value }))} /></div>
                <div><Label>Email</Label><Input value={account.email} onChange={(e) => setAccount((p) => ({ ...p, email: e.target.value }))} /></div>
                <div><Label>Phone</Label><Input value={account.phone} onChange={(e) => setAccount((p) => ({ ...p, phone: e.target.value }))} /></div>
                <Button onClick={saveAccount} disabled={saving}>
                  {saving ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null} Save Changes
                </Button>
                <div className="pt-4 border-t border-border space-y-3">
                  <h3 className="font-semibold text-sm">Change Password</h3>
                  <div><Label>Current Password</Label><Input type="password" value={pwd.current} onChange={(e) => setPwd((p) => ({ ...p, current: e.target.value }))} /></div>
                  <div><Label>New Password</Label><Input type="password" value={pwd.newPwd} onChange={(e) => setPwd((p) => ({ ...p, newPwd: e.target.value }))} /></div>
                  <div><Label>Confirm New Password</Label><Input type="password" value={pwd.confirm} onChange={(e) => setPwd((p) => ({ ...p, confirm: e.target.value }))} /></div>
                  <Button variant="secondary" onClick={changePassword} disabled={saving}>Update Password</Button>
                </div>
              </div>
            )}

            {/* NOTIFICATIONS */}
            {tab === "Notifications" && (
              <div className="space-y-4">
                <h2 className="font-bold">Email Notifications</h2>
                {([
                  ["jobAlerts",         "Email me when new jobs match my profile"],
                  ["analysisComplete",  "Email me analysis completion results"],
                  ["weeklyDigest",      "Weekly job digest"],
                  ["productUpdates",    "Product updates"],
                ] as [keyof NotifSettings, string][]).map(([key, label]) => (
                  <div key={key} className="flex items-center justify-between py-2 border-b border-border">
                    <span className="text-sm">{label}</span>
                    <Switch checked={notifs[key]} onCheckedChange={(v) => saveNotifs({ ...notifs, [key]: v })} />
                  </div>
                ))}
              </div>
            )}

            {/* PRIVACY */}
            {tab === "Privacy" && (
              <div className="space-y-4">
                <h2 className="font-bold">Privacy</h2>
                <div className="flex items-center justify-between py-2 border-b border-border">
                  <span className="text-sm">Make profile visible to recruiters</span>
                  <Switch checked={privacy.visibleToRecruiters} onCheckedChange={(v) => savePrivacy({ ...privacy, visibleToRecruiters: v })} />
                </div>
                <div className="flex items-center justify-between py-2 border-b border-border">
                  <span className="text-sm">Allow data use for model improvement</span>
                  <Switch checked={privacy.allowDataUse} onCheckedChange={(v) => savePrivacy({ ...privacy, allowDataUse: v })} />
                </div>
                <Button variant="secondary" onClick={downloadData}>Download my data</Button>
              </div>
            )}

            {/* DANGER ZONE */}
            {tab === "Danger Zone" && (
              <div className="border border-danger/30 rounded-lg p-5 bg-danger/5">
                <h2 className="font-bold text-danger">Delete Account</h2>
                <p className="text-sm text-muted-foreground mt-1">This action cannot be undone. All your data will be permanently deleted.</p>
                <Dialog>
                  <DialogTrigger asChild>
                    <Button variant="destructive" className="mt-4">Delete Account</Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Are you absolutely sure?</DialogTitle>
                      <DialogDescription>
                        Type <span className="font-mono font-bold text-foreground">DELETE</span> to confirm permanent deletion.
                      </DialogDescription>
                    </DialogHeader>
                    <Input value={confirmText} onChange={(e) => setConfirmText(e.target.value)} placeholder="Type DELETE" />
                    <DialogFooter>
                      <Button variant="destructive" disabled={confirmText !== "DELETE"} onClick={deleteAccount}>
                        Permanently Delete
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
