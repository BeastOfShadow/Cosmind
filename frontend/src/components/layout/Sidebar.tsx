import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  MessageSquare,
  Map as MapIcon,
  Database,
  PenTool,
  FolderSync,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  Loader2,
  PanelLeftClose,
  PanelLeftOpen,
} from "lucide-react";
import { useProcessStream } from "../../hooks/useProcessStream";
import Modal from "./Modal";

const NAV = [
  { to: "/", label: "Chat RAG", Icon: MessageSquare },
  { to: "/map", label: "3D Map", Icon: MapIcon },
  { to: "/vault", label: "Explore DB", Icon: Database },
  { to: "/editor", label: "Write Note", Icon: PenTool },
];

type Pending = "sync" | "process" | null;

const CONFIRM: Record<Exclude<Pending, null>, { title: string; body: string; cta: string }> = {
  sync: {
    title: "Sync database?",
    body: "Aligns ChromaDB with the notes/ and inbox/ folders: adds new notes, updates modified ones, removes deleted ones.",
    cta: "Sync",
  },
  process: {
    title: "Process inbox?",
    body: "Runs the LLM pipeline over every note in raw_notes/. This can take a while and uses API tokens.",
    cta: "Process",
  },
};

// Left navigation rail + pipeline/sync action buttons with confirm + status modals.
export default function Sidebar() {
  const location = useLocation();
  const { actionStatus, processing, processMsg, syncState, runProcess, runSync, dismissSync, dismissAction } =
    useProcessStream();
  const [pending, setPending] = useState<Pending>(null);
  const [collapsed, setCollapsed] = useState(
    () => localStorage.getItem("sidebar-collapsed") === "1"
  );

  const toggleCollapsed = () =>
    setCollapsed((c) => {
      localStorage.setItem("sidebar-collapsed", c ? "0" : "1");
      return !c;
    });

  const navClass = (path: string) =>
    `flex items-center gap-3 p-3 rounded-lg transition-colors ${
      collapsed ? "justify-center" : ""
    } ${
      location.pathname === path
        ? "bg-indigo-600/20 text-indigo-400 border border-indigo-500/30"
        : "hover:bg-slate-800 text-slate-300"
    }`;

  const confirm = () => {
    const action = pending;
    setPending(null);
    if (action === "sync") runSync();
    else if (action === "process") runProcess();
  };

  return (
    <div
      className={`bg-slate-950 p-4 flex flex-col border-r border-slate-800 flex-shrink-0 transition-all duration-200 ${
        collapsed ? "w-20" : "w-64"
      }`}
    >
      <div className={`flex items-center mb-8 ${collapsed ? "justify-center" : "justify-between"}`}>
        {!collapsed && <h1 className="text-xl font-bold text-indigo-400">🧠 Cosmind</h1>}
        <button
          onClick={toggleCollapsed}
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          className="p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800"
        >
          {collapsed ? <PanelLeftOpen size={20} /> : <PanelLeftClose size={20} />}
        </button>
      </div>

      <nav className="flex flex-col gap-2 mb-10">
        {NAV.map(({ to, label, Icon }) => (
          <Link key={to} to={to} className={navClass(to)} title={collapsed ? label : undefined}>
            <Icon size={18} /> {!collapsed && label}
          </Link>
        ))}
      </nav>

      <div className="mt-auto flex flex-col gap-3 border-t border-slate-800 pt-6">
        <button
          onClick={() => setPending("process")}
          disabled={processing}
          title={processing ? processMsg : "Process Inbox"}
          className="flex items-center justify-center gap-2 bg-slate-800 hover:bg-slate-700 disabled:hover:bg-slate-800 disabled:cursor-progress p-3 rounded-lg border border-slate-700 text-sm overflow-hidden"
        >
          <FolderSync
            size={16}
            className={`text-amber-400 shrink-0 ${processing ? "animate-spin" : ""}`}
          />
          {!collapsed && <span className="truncate">{processing ? processMsg : "Process Inbox"}</span>}
        </button>
        <button
          onClick={() => setPending("sync")}
          disabled={syncState?.phase === "running"}
          title={syncState?.phase === "running" ? "Syncing..." : "Sync Database"}
          className="flex items-center justify-center gap-2 bg-slate-800 hover:bg-slate-700 disabled:hover:bg-slate-800 disabled:cursor-progress p-3 rounded-lg border border-slate-700 text-sm"
        >
          <RefreshCw
            size={16}
            className={`text-emerald-400 shrink-0 ${syncState?.phase === "running" ? "animate-spin" : ""}`}
          />
          {!collapsed && (syncState?.phase === "running" ? "Syncing..." : "Sync Database")}
        </button>
      </div>

      {/* Confirm dialog (centered) */}
      <Modal open={pending !== null} onClose={() => setPending(null)} title={pending ? CONFIRM[pending].title : ""}>
        {pending && (
          <>
            <p className="text-sm text-slate-300">{CONFIRM[pending].body}</p>
            <div className="mt-6 flex justify-end gap-2">
              <button
                onClick={() => setPending(null)}
                className="px-4 py-2 rounded-lg text-sm text-slate-300 hover:bg-slate-800 border border-slate-700"
              >
                Cancel
              </button>
              <button
                onClick={confirm}
                className="px-4 py-2 rounded-lg text-sm font-medium bg-indigo-600 hover:bg-indigo-500 text-white"
              >
                {CONFIRM[pending].cta}
              </button>
            </div>
          </>
        )}
      </Modal>

      {/* Process inbox result (centered) */}
      <Modal
        open={!processing && !!actionStatus}
        onClose={dismissAction}
        title="Process inbox"
      >
        <div className="flex items-start gap-2 text-slate-200 text-sm">
          <CheckCircle2 size={20} className="text-amber-400 shrink-0" />
          <span>{actionStatus}</span>
        </div>
      </Modal>

      {/* Sync result (centered) */}
      <Modal
        open={syncState !== null}
        onClose={syncState?.phase === "running" ? undefined : dismissSync}
        title={
          syncState?.phase === "running"
            ? "Syncing database..."
            : syncState?.phase === "error"
            ? "Sync failed"
            : "Sync complete"
        }
      >
        {syncState?.phase === "running" && (
          <div className="flex items-center gap-3 text-slate-300 text-sm">
            <Loader2 size={20} className="animate-spin text-emerald-400" />
            Aligning ChromaDB with your notes...
          </div>
        )}

        {syncState?.phase === "success" && (
          <div>
            <div className="flex items-center gap-2 text-emerald-300 text-sm">
              <CheckCircle2 size={20} className="text-emerald-400" />
              {syncState.message}
            </div>
            {syncState.stats && (
              <>
                <div className="mt-4 grid grid-cols-3 gap-2 text-center">
                  <div className="rounded-lg bg-slate-800 p-3">
                    <div className="text-emerald-400 font-bold text-lg">{syncState.stats.added}</div>
                    <div className="text-xs text-slate-400">new</div>
                  </div>
                  <div className="rounded-lg bg-slate-800 p-3">
                    <div className="text-amber-400 font-bold text-lg">{syncState.stats.updated}</div>
                    <div className="text-xs text-slate-400">updated</div>
                  </div>
                  <div className="rounded-lg bg-slate-800 p-3">
                    <div className="text-red-400 font-bold text-lg">{syncState.stats.deleted}</div>
                    <div className="text-xs text-slate-400">deleted</div>
                  </div>
                </div>
                <div className="mt-3 text-center text-xs text-slate-400">
                  {syncState.stats.total} notes in database
                </div>
              </>
            )}
          </div>
        )}

        {syncState?.phase === "error" && (
          <div className="flex items-start gap-2 text-red-200 text-sm">
            <AlertCircle size={20} className="text-red-400 shrink-0" />
            <span>{syncState.message}</span>
          </div>
        )}
      </Modal>
    </div>
  );
}
