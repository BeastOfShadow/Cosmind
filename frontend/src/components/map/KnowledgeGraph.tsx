/* react-force-graph-2d exposes loosely-typed node/link/canvas callbacks, so
   `any` is unavoidable at this boundary. */
/* eslint-disable @typescript-eslint/no-explicit-any */
import { useRef, useMemo, useState, useEffect, useCallback } from "react";
import ForceGraph2D from "react-force-graph-2d";
import type { GraphLink, GraphNode } from "../../types";

interface KnowledgeGraphProps {
  graph: { nodes: GraphNode[]; links: GraphLink[] };
}

// Force-directed knowledge graph. Nodes are sized/colored by their connection
// count (hubs stand out) and labeled; links are weighted by similarity.
export default function KnowledgeGraph({ graph }: KnowledgeGraphProps) {
  const boxRef = useRef<HTMLDivElement>(null);
  const fgRef = useRef<any>(null);
  const [dims, setDims] = useState({ width: 800, height: 600 });

  // The force graph does not auto-fit its parent, so we measure it ourselves.
  useEffect(() => {
    const el = boxRef.current;
    if (!el) return;
    const ro = new ResizeObserver((entries) => {
      const { width, height } = entries[0].contentRect;
      setDims({ width, height });
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  const degreeMap = useMemo<Record<string, number>>(() => {
    const m: Record<string, number> = {};
    for (const l of graph.links) {
      const s = typeof l.source === "object" ? (l.source as any).id : l.source;
      const t = typeof l.target === "object" ? (l.target as any).id : l.target;
      m[s] = (m[s] || 0) + 1;
      m[t] = (m[t] || 0) + 1;
    }
    return m;
  }, [graph]);

  const maxDeg = useMemo(
    () => Math.max(1, ...Object.values(degreeMap)),
    [degreeMap],
  );

  const radius = useCallback(
    (id: string) => 3 + ((degreeMap[id] || 0) / maxDeg) * 8,
    [degreeMap, maxDeg],
  );

  const drawNode = useCallback(
    (node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
      const deg = degreeMap[node.id] || 0;
      const r = radius(node.id);
      const intensity = 0.4 + 0.6 * (deg / maxDeg);
      ctx.beginPath();
      ctx.arc(node.x, node.y, r, 0, 2 * Math.PI);
      ctx.fillStyle = `rgba(129,140,248,${intensity})`; // indigo, brighter = more connected
      ctx.fill();
      ctx.lineWidth = 0.6;
      ctx.strokeStyle = "rgba(199,210,254,0.7)";
      ctx.stroke();

      const label = String(node.name || "").replace(/\.md$/, "");
      const shown = label.length > 24 ? label.slice(0, 23) + "…" : label;
      const fontSize = Math.max(10 / globalScale, 1.5);
      ctx.font = `${fontSize}px Inter, sans-serif`;
      ctx.textAlign = "center";
      ctx.textBaseline = "top";
      ctx.fillStyle = "rgba(203,213,225,0.9)";
      ctx.fillText(shown, node.x, node.y + r + 1);
    },
    [degreeMap, maxDeg, radius],
  );

  return (
    <div ref={boxRef} className="w-full h-full">
      <ForceGraph2D
        ref={fgRef}
        graphData={graph}
        width={dims.width}
        height={dims.height}
        backgroundColor="#020617"
        nodeLabel={(n: any) => n.preview}
        nodeRelSize={1}
        nodeCanvasObject={drawNode}
        nodePointerAreaPaint={(node: any, color: string, ctx: CanvasRenderingContext2D) => {
          const r = radius(node.id);
          ctx.fillStyle = color;
          ctx.beginPath();
          ctx.arc(node.x, node.y, r + 2, 0, 2 * Math.PI);
          ctx.fill();
        }}
        linkColor={(l: any) => `rgba(99,102,241,${0.15 + 0.55 * (l.similarity ?? 0.5)})`}
        linkWidth={(l: any) => 0.5 + 12 * Math.max(0, (l.similarity ?? 0.75) - 0.75)}
        cooldownTicks={120}
        onEngineStop={() => fgRef.current?.zoomToFit(400, 50)}
      />
      <div className="absolute bottom-4 left-4 bg-slate-900/80 backdrop-blur-md border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-400 pointer-events-none">
        <div className="font-semibold text-slate-300 mb-1">Knowledge Graph</div>
        <div>● node size = connections (hubs)</div>
        <div>— line thickness = similarity (&gt; 75%)</div>
      </div>
    </div>
  );
}
