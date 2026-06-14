import { Edit3, Columns, Eye } from "lucide-react";
import type { ViewMode } from "../../types";

interface ViewModeToggleProps {
  viewMode: ViewMode;
  setViewMode: (m: ViewMode) => void;
}

const MODES: { id: ViewMode; title: string; Icon: typeof Edit3; mx?: boolean }[] = [
  { id: "edit", title: "Text editor", Icon: Edit3 },
  { id: "split", title: "Split view", Icon: Columns, mx: true },
  { id: "preview", title: "Read only", Icon: Eye },
];

// Editor / split / preview switcher.
export default function ViewModeToggle({ viewMode, setViewMode }: ViewModeToggleProps) {
  return (
    <div className="flex bg-slate-800 p-1.5 rounded-lg border border-slate-700 shadow-sm z-10 shrink-0">
      {MODES.map(({ id, title, Icon, mx }) => (
        <button
          key={id}
          onClick={() => setViewMode(id)}
          title={title}
          className={`p-2 rounded-md transition-colors ${mx ? "mx-1" : ""} ${
            viewMode === id
              ? "bg-indigo-600 text-white shadow-md text-xs"
              : "text-slate-400 hover:text-slate-200"
          }`}
        >
          <Icon size={18} />
        </button>
      ))}
    </div>
  );
}
