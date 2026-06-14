import { Eye } from "lucide-react";

export type MapView = "2d" | "3d" | "graph";

interface ViewTabsProps {
  view: MapView;
  setView: (v: MapView) => void;
  showLabels: boolean;
  setShowLabels: (v: boolean) => void;
}

const TABS: { id: MapView; label: string }[] = [
  { id: "2d", label: "Clusters (2D)" },
  { id: "3d", label: "Galaxy (3D)" },
  { id: "graph", label: "Neural Network" },
];

// Header controls for the map: show/hide labels (2D/3D only) + view switcher.
export default function ViewTabs({ view, setView, showLabels, setShowLabels }: ViewTabsProps) {
  return (
    <div className="flex items-center gap-4">
      {(view === "2d" || view === "3d") && (
        <button
          onClick={() => setShowLabels(!showLabels)}
          className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-md text-sm text-slate-300 transition-colors"
        >
          <Eye size={16} className={showLabels ? "text-indigo-400" : ""} />
          {showLabels ? "Hide Names" : "Show Names"}
        </button>
      )}

      <div className="flex bg-slate-800 rounded-lg p-1 border border-slate-700">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setView(tab.id)}
            className={`px-4 py-1.5 rounded-md text-sm transition-colors ${
              view === tab.id
                ? "bg-indigo-600 text-white shadow"
                : "text-slate-400 hover:text-white"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>
    </div>
  );
}
