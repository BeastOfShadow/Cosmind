import { Link, useLocation } from "react-router-dom";
import {
  MessageSquare,
  Map as MapIcon,
  Database,
  PenTool,
  FolderSync,
  RefreshCw,
} from "lucide-react";
import { useProcessStream } from "../../hooks/useProcessStream";

const NAV = [
  { to: "/", label: "Chat RAG", Icon: MessageSquare },
  { to: "/map", label: "3D Map", Icon: MapIcon },
  { to: "/vault", label: "Explore DB", Icon: Database },
  { to: "/editor", label: "Write Note", Icon: PenTool },
];

// Left navigation rail + pipeline/sync action buttons with live status.
export default function Sidebar() {
  const location = useLocation();
  const { actionStatus, processing, processMsg, runProcess, runSync } = useProcessStream();

  const navClass = (path: string) =>
    `flex items-center gap-3 p-3 rounded-lg transition-colors ${
      location.pathname === path
        ? "bg-indigo-600/20 text-indigo-400 border border-indigo-500/30"
        : "hover:bg-slate-800 text-slate-300"
    }`;

  return (
    <div className="w-64 bg-slate-950 p-4 flex flex-col border-r border-slate-800 flex-shrink-0">
      <h1 className="text-xl font-bold mb-8 text-center text-indigo-400">🧠 Cosmind</h1>

      <nav className="flex flex-col gap-2 mb-10">
        {NAV.map(({ to, label, Icon }) => (
          <Link key={to} to={to} className={navClass(to)}>
            <Icon size={18} /> {label}
          </Link>
        ))}
      </nav>

      <div className="mt-auto flex flex-col gap-3 border-t border-slate-800 pt-6">
        <button
          onClick={runProcess}
          disabled={processing}
          title={processing ? processMsg : "Process Inbox"}
          className="flex items-center justify-center gap-2 bg-slate-800 hover:bg-slate-700 disabled:hover:bg-slate-800 disabled:cursor-progress p-3 rounded-lg border border-slate-700 text-sm overflow-hidden"
        >
          <FolderSync
            size={16}
            className={`text-amber-400 shrink-0 ${processing ? "animate-spin" : ""}`}
          />
          <span className="truncate">{processing ? processMsg : "Process Inbox"}</span>
        </button>
        <button
          onClick={runSync}
          className="flex items-center justify-center gap-2 bg-slate-800 hover:bg-slate-700 p-3 rounded-lg border border-slate-700 text-sm"
        >
          <RefreshCw size={16} className="text-emerald-400" /> Sync Database
        </button>
      </div>

      {actionStatus && (
        <div className="mt-4 bg-slate-800 text-xs p-3 rounded text-amber-200 border border-amber-900 text-center">
          {actionStatus}
        </div>
      )}
    </div>
  );
}
