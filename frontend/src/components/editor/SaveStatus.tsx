import type { SaveStatus as Status } from "../../types";

const DOT: Record<Status, string> = {
  saving: "bg-amber-500 animate-ping",
  saved: "bg-emerald-500",
  idle: "bg-slate-700",
  error: "bg-slate-700",
};

// Auto-save indicator (dot + label) shown in the editor toolbar.
export default function SaveStatus({ status }: { status: Status }) {
  return (
    <div className="flex items-center gap-2 text-sm font-medium">
      <div className={`w-2 h-2 rounded-full ${DOT[status]}`} />
      {status === "saving" && <span className="text-slate-400">Saving...</span>}
      {status === "saved" && (
        <span className="text-emerald-400">All changes saved to Raw Notes</span>
      )}
      {status === "idle" && <span className="text-slate-500">Ready in raw_notes/</span>}
      {status === "error" && <span className="text-red-400">Connection error</span>}
    </div>
  );
}
