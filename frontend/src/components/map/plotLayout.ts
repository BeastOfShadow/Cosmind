// Shared transparent Plotly layout used by both the 2D and 3D views.
export const basePlotLayout: Record<string, unknown> = {
  autosize: true,
  margin: { l: 0, r: 0, b: 0, t: 0 },
  paper_bgcolor: "rgba(0,0,0,0)",
  plot_bgcolor: "rgba(0,0,0,0)",
  legend: { font: { color: "#cbd5e1" } },
};
