import { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { ArrowLeft, FileText, Layers, HardDrive, Sparkles, ChevronRight } from "lucide-react";
import { API_URL } from "../lib/config";
import Markdown from "../components/Markdown";
import type { NoteDetail } from "../types";

// Rich detail view for a single note: full Markdown from disk, its vector-DB
// chunk breakdown, and the most semantically similar notes.
export default function NoteDetailPage() {
  const { source = "" } = useParams();
  const navigate = useNavigate();
  const [note, setNote] = useState<NoteDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    setLoading(true);
    setNotFound(false);
    fetch(`${API_URL}/note/${encodeURIComponent(source)}`)
      .then((res) => {
        if (res.status === 404) {
          setNotFound(true);
          return null;
        }
        return res.json();
      })
      .then((data) => data && setNote(data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [source]);

  return (
    <div className="flex-1 flex flex-col max-w-5xl mx-auto w-full p-6 h-full min-h-0">
      {/* Back */}
      <button
        onClick={() => navigate("/vault")}
        className="flex items-center gap-1.5 text-sm text-slate-400 hover:text-slate-200 transition-colors mb-4 shrink-0 w-fit"
      >
        <ArrowLeft size={16} /> Explore Database
      </button>

      {loading ? (
        <p className="text-slate-400">Loading note...</p>
      ) : notFound || !note ? (
        <div className="flex-1 flex flex-col items-center justify-center text-slate-500">
          <FileText size={40} className="mb-3 opacity-50" />
          <p>Note "{source}" not found.</p>
        </div>
      ) : (
        <div className="flex-1 min-h-0 grid grid-cols-1 lg:grid-cols-[1fr_18rem] gap-6 overflow-hidden">
          {/* Main content */}
          <div className="flex flex-col min-h-0">
            <header className="mb-4 shrink-0">
              <h1 className="text-2xl font-semibold text-slate-100 break-words flex items-center gap-2">
                <FileText size={22} className="text-indigo-400 shrink-0" />
                {note.source}
              </h1>
              <div className="flex items-center gap-3 mt-2 text-xs text-slate-400">
                <span className="flex items-center gap-1.5">
                  <Layers size={13} className="text-indigo-400" />
                  {note.chunks.length} chunk{note.chunks.length === 1 ? "" : "s"}
                </span>
                <span className="flex items-center gap-1.5">
                  <HardDrive size={13} className={note.on_disk ? "text-emerald-400" : "text-amber-400"} />
                  {note.on_disk ? "on disk" : "reconstructed from DB"}
                </span>
              </div>
            </header>

            <article className="flex-1 min-h-0 overflow-y-auto pr-3 rounded-xl border border-slate-700/70 bg-slate-800/30 p-5">
              <div className="prose prose-invert prose-sm max-w-none prose-headings:text-slate-100 prose-a:text-indigo-400 prose-code:text-indigo-300 prose-pre:bg-slate-900/70">
                <Markdown content={note.content} imgClassName="rounded-lg max-w-full" />
              </div>
            </article>
          </div>

          {/* Sidebar: chunks + similar */}
          <aside className="flex flex-col gap-5 min-h-0 overflow-y-auto pr-1">
            {/* Chunk breakdown */}
            <section>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1.5">
                <Layers size={13} /> Chunk breakdown
              </h3>
              <div className="space-y-2">
                {note.chunks.map((c) => (
                  <div
                    key={c.chunk_index}
                    className="bg-slate-800/40 border border-slate-700/60 rounded-lg p-3"
                  >
                    <div className="text-[10px] font-bold text-indigo-400/90 uppercase tracking-wider mb-1.5 tabular-nums">
                      chunk {c.chunk_index + 1}/{c.chunk_total}
                    </div>
                    <p className="text-xs text-slate-400 leading-relaxed line-clamp-4">
                      {c.content}
                    </p>
                  </div>
                ))}
              </div>
            </section>

            {/* Similar notes */}
            {note.similar.length > 0 && (
              <section>
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1.5">
                  <Sparkles size={13} /> Similar notes
                </h3>
                <div className="space-y-1.5">
                  {note.similar.map((s) => (
                    <Link
                      key={s.source}
                      to={`/vault/${encodeURIComponent(s.source)}`}
                      className="flex items-center gap-2 bg-slate-800/40 hover:bg-slate-800 border border-slate-700/60 hover:border-indigo-500/50 rounded-lg px-3 py-2 transition-colors group"
                    >
                      <FileText size={13} className="text-indigo-400/80 shrink-0" />
                      <span className="text-xs text-slate-300 truncate flex-1">{s.source}</span>
                      <span className="text-[10px] text-slate-500 tabular-nums shrink-0">
                        {(s.score * 100).toFixed(0)}%
                      </span>
                      <ChevronRight size={13} className="text-slate-600 group-hover:text-indigo-400 shrink-0" />
                    </Link>
                  ))}
                </div>
              </section>
            )}
          </aside>
        </div>
      )}
    </div>
  );
}
