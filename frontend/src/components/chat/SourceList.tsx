import { Database } from "lucide-react";
import type { Source } from "../../types";

// Collapsible list of the vault sources a RAG answer was grounded on.
export default function SourceList({ sources }: { sources: Source[] }) {
  return (
    <div className="mt-4 pt-3 border-t border-slate-700/50">
      <div className="flex items-center gap-2 mb-3">
        <Database size={12} className="text-slate-400" />
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Sources used:
        </span>
      </div>
      <div className="flex flex-col gap-2">
        {sources.map((src, idx) => (
          <details
            key={idx}
            className="group bg-slate-900/50 border border-slate-700/50 rounded-lg overflow-hidden"
          >
            <summary className="flex items-center gap-2 text-xs text-indigo-300 px-3 py-2 cursor-pointer hover:bg-slate-800 transition-colors list-none">
              <span className="w-4 h-4 flex items-center justify-center bg-slate-800 rounded transition-transform group-open:rotate-90">
                ▶
              </span>
              <span className="font-medium">{src.source}</span>
            </summary>
            <div className="px-4 py-3 text-xs text-slate-400 border-t border-slate-700/50 bg-slate-900/80 whitespace-pre-wrap leading-relaxed">
              {src.content}
            </div>
          </details>
        ))}
      </div>
    </div>
  );
}
