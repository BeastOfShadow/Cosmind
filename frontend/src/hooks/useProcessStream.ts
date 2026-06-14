import { useState } from "react";
import { API_URL } from "../lib/config";

// Drives the sidebar's "Process Inbox" (live SSE progress) and "Sync Database"
// actions. Keeps the streaming/reader plumbing out of the UI components.
export type SyncState =
  | { phase: "running" }
  | { phase: "success"; message: string; stats: { added: number; updated: number; deleted: number; total: number } }
  | { phase: "error"; message: string }
  | null;

export function useProcessStream() {
  const [actionStatus, setActionStatus] = useState<string | null>(null);
  const [processing, setProcessing] = useState(false);
  const [processMsg, setProcessMsg] = useState("Process Inbox");
  const [syncState, setSyncState] = useState<SyncState>(null);

  const runSync = async () => {
    setSyncState({ phase: "running" });
    try {
      const res = await fetch(`${API_URL}/sync`, { method: "POST" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setSyncState({ phase: "success", message: data.message || "Sync finished", stats: data.stats });
      setTimeout(() => setSyncState(null), 6000);
    } catch (e) {
      setSyncState({ phase: "error", message: e instanceof Error ? e.message : "Sync failed" });
    }
  };

  const dismissSync = () => setSyncState(null);

  // Reads the Server-Sent Events stream and surfaces the latest progress line
  // (which note/agent the LLM is working on, mirroring the Docker logs).
  const runProcess = async () => {
    if (processing) return;
    setProcessing(true);
    setProcessMsg("🚀 Starting...");
    setActionStatus(null);
    try {
      const res = await fetch(`${API_URL}/process/stream`, { method: "POST" });
      if (!res.body) throw new Error("No stream");
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let last = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split("\n\n");
        buffer = parts.pop() || "";
        for (const part of parts) {
          const line = part.replace(/^data:\s?/, "").trim();
          if (!line) continue;
          try {
            const evt = JSON.parse(line);
            last = evt.message;
            if (evt.type === "done") setActionStatus(evt.message);
            else setProcessMsg(evt.message);
          } catch {
            /* ignore keep-alive / partial frames */
          }
        }
      }
      setActionStatus(last || "✅ Done");
    } catch {
      setActionStatus("❌ Error");
    } finally {
      setProcessing(false);
      setProcessMsg("Process Inbox");
      setTimeout(() => setActionStatus(null), 5000);
    }
  };

  const dismissAction = () => setActionStatus(null);

  return { actionStatus, processing, processMsg, syncState, runProcess, runSync, dismissSync, dismissAction };
}
