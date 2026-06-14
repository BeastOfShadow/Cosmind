import { useState, useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { Database, Search, FileText, Layers, ChevronRight, X } from "lucide-react";
import { API_URL } from "../lib/config";
import type { VaultData, VaultDoc } from "../types";

interface SourceGroup {
  source: string;
  chunks: VaultDoc[];
  preview: string;
}

// Browse the notes vectorized in ChromaDB. Each note is searchable and opens
// its full detail view on click.
export default function VaultPage() {
  const navigate = useNavigate();
  const [vaultData, setVaultData] = useState<VaultData>({ documents: [], total: 0 });
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");

  useEffect(() => {
    fetch(`${API_URL}/vault`)
      .then((res) => res.json())
      .then((data) => setVaultData(data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  // Filter by source name OR chunk content, then group chunks by source note.
  const groups = useMemo<SourceGroup[]>(() => {
    const q = query.trim().toLowerCase();
    const docs = q
      ? vaultData.documents.filter(
          (d) => d.source.toLowerCase().includes(q) || d.content.toLowerCase().includes(q)
        )
      : vaultData.documents;

    const map = new Map<string, VaultDoc[]>();
    for (const d of docs) {
      const list = map.get(d.source) ?? [];
      list.push(d);
      map.set(d.source, list);
    }
    return [...map.entries()]
      .map(([source, chunks]) => {
        const ordered = [...chunks].sort((a, b) => a.chunk_index - b.chunk_index);
        return { source, chunks: ordered, preview: ordered[0]?.preview ?? "" };
      })
      .sort((a, b) => a.source.localeCompare(b.source));
  }, [vaultData.documents, query]);

  const filteredChunks = groups.reduce((n, g) => n + g.chunks.length, 0);
  const sourceCount = vaultData.sources ?? groups.length;

  return (
    <div className="flex-1 flex flex-col max-w-5xl mx-auto w-full p-6 h-full min-h-0">
      <header className="mb-5 shrink-0">
        <h2 className="text-2xl font-semibold opacity-80">Explore Database</h2>
        <p className="text-slate-400 mt-1 text-sm">
          {loading ? (
            "Reading DB..."
          ) : (
            <span className="flex items-center gap-4">
              <span className="flex items-center gap-1.5">
                <FileText size={14} className="text-indigo-400" />
                {sourceCount} note{sourceCount === 1 ? "" : "s"}
              </span>
              <span className="flex items-center gap-1.5">
                <Layers size={14} className="text-indigo-400" />
                {vaultData.total} chunk{vaultData.total === 1 ? "" : "s"}
              </span>
            </span>
          )}
        </p>
      </header>

      {/* Search */}
      {!loading && vaultData.total > 0 && (
        <div className="relative mb-4 shrink-0">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search notes or content..."
            className="w-full bg-slate-800/60 border border-slate-700 rounded-lg pl-9 pr-9 py-2 text-sm text-slate-200 placeholder:text-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
          />
          {query && (
            <button
              onClick={() => setQuery("")}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
              title="Clear"
            >
              <X size={15} />
            </button>
          )}
        </div>
      )}

      {vaultData.total === 0 && !loading ? (
        <div className="flex-1 flex flex-col items-center justify-center border-2 border-dashed border-slate-700 rounded-xl opacity-50">
          <Database size={48} className="mb-4" />
          <p>The database is empty. Process some notes to get started.</p>
        </div>
      ) : query && filteredChunks === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center text-slate-500">
          <Search size={40} className="mb-3 opacity-50" />
          <p>No notes match "{query}".</p>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto pr-1 space-y-2.5 min-h-0">
          {groups.map((g) => (
            <button
              key={g.source}
              onClick={() => navigate(`/vault/${encodeURIComponent(g.source)}`)}
              className="w-full text-left flex items-center gap-3 rounded-xl border border-slate-700/70 bg-slate-800/30 px-4 py-3.5 hover:bg-slate-800/60 hover:border-indigo-500/50 transition-all hover:shadow-lg hover:shadow-indigo-500/5 group"
            >
              <span className="shrink-0 flex items-center justify-center w-9 h-9 rounded-lg bg-indigo-500/10 text-indigo-400">
                <FileText size={17} />
              </span>
              <span className="flex-1 min-w-0">
                <span className="block text-sm font-medium text-slate-100 truncate">{g.source}</span>
                <span className="block text-xs text-slate-500 truncate mt-0.5">{g.preview}</span>
              </span>
              <span className="text-[11px] font-medium text-slate-300 bg-slate-700/60 rounded-full px-2.5 py-1 shrink-0 tabular-nums">
                {g.chunks.length} chunk{g.chunks.length === 1 ? "" : "s"}
              </span>
              <ChevronRight
                size={16}
                className="text-slate-600 group-hover:text-indigo-400 shrink-0 transition-colors"
              />
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
