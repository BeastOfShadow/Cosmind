import PlotlyPlot from "react-plotly.js";
import type { MapTrace } from "../../types";
import { basePlotLayout } from "./plotLayout";

// react-plotly.js ships its component as a CJS default export under ESM interop.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const Plot = (PlotlyPlot as any).default || PlotlyPlot;

const axis = {
  color: "#64748b",
  gridcolor: "#1e293b",
  zerolinecolor: "#334155",
  backgroundcolor: "rgba(0,0,0,0)",
};

// 3D PCA scatter — the "galaxy" view, one trace per source file.
export default function GalaxyPlot({
  traces,
  showLabels,
}: {
  traces: MapTrace[];
  showLabels: boolean;
}) {
  const data = traces.map((trace) => ({
    x: trace.x,
    y: trace.y,
    z: trace.z,
    text: trace.texts,
    name: trace.name,
    mode: showLabels ? "markers+text" : "markers",
    type: "scatter3d",
    textposition: "top center",
    textfont: { size: 10, color: "#fff" },
    marker: { size: 6, opacity: 0.9 },
    hoverinfo: "text",
  }));

  return (
    <Plot
      data={data}
      layout={{
        ...basePlotLayout,
        scene: { xaxis: axis, yaxis: axis, zaxis: axis, bgcolor: "rgba(0,0,0,0)" },
      }}
      useResizeHandler={true}
      style={{ width: "100%", height: "100%", minHeight: "500px" }}
      config={{ displayModeBar: false }}
    />
  );
}
