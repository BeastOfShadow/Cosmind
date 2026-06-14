import { useState, useEffect } from "react";
import { Database } from "lucide-react";
import { API_URL } from "../lib/config";
import type { MapData } from "../types";
import ViewTabs, { type MapView } from "../components/map/ViewTabs";
import ClusterPlot from "../components/map/ClusterPlot";
import GalaxyPlot from "../components/map/GalaxyPlot";
import KnowledgeGraph from "../components/map/KnowledgeGraph";

// Analytics dashboard: semantic clusters (2D), galaxy (3D), knowledge graph.
export default function MapPage() {
  const [mapData, setMapData] = useState<MapData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [view, setView] = useState<MapView>("2d");
  const [showLabels, setShowLabels] = useState(false);

  useEffect(() => {
    fetch(`${API_URL}/visualize`)
      .then((res) => res.json())
      .then((data) => {
        if (data.error) setError(data.error);
        else setMapData(data);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading)
    return (
      <div className="flex-1 flex items-center justify-center animate-pulse">
        Running vector analysis...
      </div>
    );
  if (error || !mapData)
    return (
      <div className="flex-1 flex flex-col items-center justify-center text-red-400 p-10">
        <Database size={48} className="mb-4 opacity-50" />
        <span>{error}</span>
      </div>
    );

  return (
    <div className="flex-1 flex flex-col p-6 h-full">
      <div className="flex justify-between items-end mb-4">
        <h2 className="text-2xl font-semibold opacity-80">Analytics Dashboard</h2>
        <ViewTabs
          view={view}
          setView={setView}
          showLabels={showLabels}
          setShowLabels={setShowLabels}
        />
      </div>

      <div className="flex-1 w-full h-full min-h-[500px] bg-slate-950 rounded-xl border border-slate-800 overflow-hidden relative shadow-2xl flex items-center justify-center">
        {view === "2d" && <ClusterPlot traces={mapData.traces2D} showLabels={showLabels} />}
        {view === "3d" && <GalaxyPlot traces={mapData.traces3D} showLabels={showLabels} />}
        {view === "graph" && <KnowledgeGraph graph={mapData.graph} />}
      </div>
    </div>
  );
}
