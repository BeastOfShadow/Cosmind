import PlotlyPlot from "react-plotly.js";
import type { MapTrace } from "../../types";
import { basePlotLayout } from "./plotLayout";

// react-plotly.js ships its component as a CJS default export under ESM interop.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const Plot = (PlotlyPlot as any).default || PlotlyPlot;

// 2D t-SNE scatter, one trace per semantic cluster (KMeans, colored by Plotly).
export default function ClusterPlot({
  traces,
  showLabels,
}: {
  traces: MapTrace[];
  showLabels: boolean;
}) {
  const data = traces.map((trace) => ({
    x: trace.x,
    y: trace.y,
    text: trace.texts, // short label shown on the marker when "Show Names" is on
    hovertext: trace.hovertexts ?? trace.texts, // rich hover (source + snippet)
    name: trace.name,
    mode: showLabels ? "markers+text" : "markers",
    type: "scatter",
    textposition: "top center",
    textfont: { size: 11, color: "#cbd5e1" },
    marker: { size: 11, opacity: 0.85, line: { width: 1, color: "rgba(2,6,23,0.6)" } },
    hoverinfo: "text",
    hoverlabel: { align: "left" },
  }));

  return (
    <Plot
      data={data}
      layout={{ ...basePlotLayout, xaxis: { visible: false }, yaxis: { visible: false } }}
      useResizeHandler={true}
      style={{ width: "100%", height: "100%", minHeight: "500px" }}
      config={{ displayModeBar: false }}
    />
  );
}
