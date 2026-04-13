import { useState, useEffect } from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  Link,
  useLocation,
} from "react-router-dom";
import {
  Send,
  Bot,
  User,
  RefreshCw,
  FolderSync,
  Map as MapIcon,
  MessageSquare,
  PenTool,
  FolderOpen,
  Database,
  Wand2,
  Search,
  CheckCircle,
  GraduationCap,
  X,
  Sparkles,
  FileText,
  Image as ImageIcon,
  Trash2,
  Eye,
  Edit3,
  Columns,
} from "lucide-react";
import ForceGraph2D from "react-force-graph-2d";
import ReactMarkdown from "react-markdown";
import PlotlyPlot from "react-plotly.js";
const Plot = (PlotlyPlot as any).default || PlotlyPlot;

const API_URL = "http://localhost:8000/api";
const ASSETS_URL = "http://localhost:8000/assets";

const SLASH_COMMANDS = [
  { id: "h1", label: "Heading 1", icon: "H1", syntax: "# " },
  { id: "h2", label: "Heading 2", icon: "H2", syntax: "## " },
  { id: "h3", label: "Heading 3", icon: "H3", syntax: "### " },
  { id: "image", label: "Image", icon: "🖼️", syntax: "![Descrizione](assets/nome_immagine.png)\n" },
  { id: "pdf", label: "PDF Embed", icon: "📄", syntax: "[Scarica PDF](assets/documento.pdf)\n" },
  { id: "todo", label: "To-do List", icon: "☑", syntax: "- [ ] " },
  { id: "list", label: "Bulleted List", icon: "•", syntax: "- " },
  { id: "quote", label: "Quote", icon: "“", syntax: "> " },
  { id: "code", label: "Code Block", icon: "<>", syntax: "```\n\n```" },
  { id: "divider", label: "Divider", icon: "—", syntax: "---\n" },
  {
    id: "ai-expand",
    label: "Amplia Conoscenza",
    icon: <Search size={14} />,
    syntax: "expand",
    type: "ai",
  },
  {
    id: "ai-validate",
    label: "Valida Fonti",
    icon: <CheckCircle size={14} />,
    syntax: "validate",
    type: "ai",
  },
  {
    id: "ai-tutor",
    label: "Aiuto & Tutor",
    icon: <GraduationCap size={14} />,
    syntax: "tutor",
    type: "ai",
  },
];

// 1. Pagina Chat
function ChatPage() {
  const [query, setQuery] = useState("");

  // AGGIUNTA 1: Abbiamo detto a React che i messaggi possono avere un array opzionale di "sources"
  const [messages, setMessages] = useState<
    {
      role: "user" | "bot";
      content: string;
      sources?: { source: string; content: string }[];
    }[]
  >([]);
  const [loading, setLoading] = useState(false);

  const askBrain = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setMessages((prev) => [...prev, { role: "user", content: query }]);
    const userQuery = query;
    setQuery("");
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userQuery }),
      });
      if (!res.ok) throw new Error(`Errore HTTP: ${res.status}`);
      const data = await res.json();

      // AGGIUNTA 2: Ora salviamo anche data.sources nel messaggio del bot!
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          content: data.answer,
          sources: data.sources, // <-- Eccole qui!
        },
      ]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        { role: "bot", content: `Errore: ${err.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full p-4 h-full">
      <div className="flex-1 overflow-y-auto mb-4 space-y-6 scrollbar-hide p-2 md:p-6">
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-slate-500 gap-4">
            <Bot size={48} className="text-indigo-500/50" />
            <p className="text-lg text-center">
              Fai una domanda al tuo Second Brain.
              <br />
              <span className="text-sm">
                Risponderà usando solo i tuoi appunti.
              </span>
            </p>
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex gap-4 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            {msg.role === "bot" && (
              <div className="w-8 h-8 rounded-full bg-indigo-600/20 flex items-center justify-center border border-indigo-500/30 flex-shrink-0 mt-1">
                <Bot size={18} className="text-indigo-400" />
              </div>
            )}

            <div
              className={`max-w-[85%] rounded-2xl p-4 ${
                msg.role === "user"
                  ? "bg-indigo-600 text-white rounded-tr-sm"
                  : "bg-slate-800 text-slate-200 rounded-tl-sm border border-slate-700/50 shadow-sm"
              }`}
            >
              {msg.role === "bot" ? (
                <div className="prose prose-invert prose-p:leading-relaxed prose-pre:bg-slate-900 prose-pre:border prose-pre:border-slate-700 prose-img:rounded-xl prose-img:max-w-full max-w-none">
                  <ReactMarkdown 
                    components={{
                      img: ({node, src, alt, ...props}) => {
                        const imgSrc = src?.startsWith('assets/') ? `${ASSETS_URL}/${src.split('assets/')[1]}` : src;
                        return <img src={imgSrc} alt={alt || ''} {...props} className="my-4" />;
                      }
                    }}
                  >{msg.content}</ReactMarkdown>
                </div>
              ) : (
                <div className="leading-relaxed whitespace-pre-wrap">
                  {msg.content}
                </div>
              )}

              {/* BOX DELLE FONTI A TENDINA */}
              {msg.role === "bot" && msg.sources && msg.sources.length > 0 && (
                <div className="mt-4 pt-3 border-t border-slate-700/50">
                  <div className="flex items-center gap-2 mb-3">
                    <Database size={12} className="text-slate-400" />
                    <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                      Fonti utilizzate:
                    </span>
                  </div>
                  <div className="flex flex-col gap-2">
                    {msg.sources.map((src, idx) => (
                      <details
                        key={idx}
                        className="group bg-slate-900/50 border border-slate-700/50 rounded-lg overflow-hidden"
                      >
                        {/* INTESTAZIONE CLICCABILE */}
                        <summary className="flex items-center gap-2 text-xs text-indigo-300 px-3 py-2 cursor-pointer hover:bg-slate-800 transition-colors list-none">
                          <span className="w-4 h-4 flex items-center justify-center bg-slate-800 rounded transition-transform group-open:rotate-90">
                            ▶
                          </span>
                          <span className="font-medium">{src.source}</span>
                        </summary>
                        {/* CONTENUTO ESPANSO */}
                        <div className="px-4 py-3 text-xs text-slate-400 border-t border-slate-700/50 bg-slate-900/80 whitespace-pre-wrap leading-relaxed">
                          {src.content}
                        </div>
                      </details>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {msg.role === "user" && (
              <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center flex-shrink-0 mt-1">
                <User size={18} className="text-slate-300" />
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex gap-4 justify-start animate-pulse">
            <div className="w-8 h-8 rounded-full bg-indigo-600/20 flex items-center justify-center border border-indigo-500/30">
              <Bot size={18} className="text-indigo-400" />
            </div>
            <div className="bg-slate-800 rounded-2xl rounded-tl-sm p-4 text-slate-400 border border-slate-700/50">
              Ricerca nel Vault in corso...
            </div>
          </div>
        )}
      </div>

      <form onSubmit={askBrain} className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Chiedi qualcosa ai tuoi appunti..."
          className="w-full bg-slate-800/50 border border-slate-700 text-slate-200 rounded-xl px-4 py-4 pr-12 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-slate-800 transition-all placeholder-slate-500"
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-700 disabled:text-slate-500 text-white rounded-lg transition-colors"
        >
          <Send size={18} />
        </button>
      </form>
    </div>
  );
}

// 2. Pagina Visualizzatore 3D (Aggiornata per la Legenda e Colori)
function MapPage() {
  const [mapData, setMapData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [view, setView] = useState<"2d" | "3d" | "graph">("2d"); // Nuova gestione Tabs
  const [showLabels, setShowLabels] = useState(false); // Stato per mostrare/nascondere le etichette

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
        Analisi Vettoriale in corso...
      </div>
    );
  if (error)
    return (
      <div className="flex-1 flex flex-col items-center justify-center text-red-400 p-10">
        <Database size={48} className="mb-4 opacity-50" />
        <span>{error}</span>
      </div>
    );

  // Tracce per il 3D
  const plotly3D = mapData.traces3D.map((trace: any) => ({
    x: trace.x,
    y: trace.y,
    z: trace.z,
    text: trace.texts,
    name: trace.name,
    mode: showLabels ? "markers+text" : "markers",
    type: "scatter3d",
    textposition: "top center",
    textfont: { size: 10, color: "#fff" }, // Migliorata leggibilità del testo
    marker: { size: 6, opacity: 0.9 },
    hoverinfo: "text",
  }));

  // Tracce per il 2D (t-SNE)
  const plotly2D = mapData.traces2D.map((trace: any) => ({
    x: trace.x,
    y: trace.y,
    text: trace.texts,
    name: trace.name,
    mode: showLabels ? "markers+text" : "markers",
    type: "scatter",
    textposition: "top center",
    textfont: { size: 11, color: "#cbd5e1" }, // Migliorata leggibilità del testo
    marker: { size: 10, opacity: 0.8 },
    hoverinfo: "text+name",
  }));

  // Layout condiviso per Plotly
  const plotLayout: any = {
    autosize: true,
    margin: { l: 0, r: 0, b: 0, t: 0 },
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    legend: { font: { color: "#cbd5e1" } },
  };

  return (
    <div className="flex-1 flex flex-col p-6 h-full">
      <div className="flex justify-between items-end mb-4">
        <h2 className="text-2xl font-semibold opacity-80">
          Dashboard Analitica
        </h2>

        <div className="flex items-center gap-4">
          {/* BOTTONE ETICHETTE (Visibile solo in 2D o 3D) */}
          {(view === "2d" || view === "3d") && (
            <button
              onClick={() => setShowLabels(!showLabels)}
              className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-md text-sm text-slate-300 transition-colors"
            >
              <Eye size={16} className={showLabels ? "text-indigo-400" : ""} />
              {showLabels ? "Nascondi Nomi" : "Mostra Nomi"}
            </button>
          )}

          {/* TABS PER CAMBIARE VISTA */}
          <div className="flex bg-slate-800 rounded-lg p-1 border border-slate-700">
            <button
              onClick={() => setView("2d")}
              className={`px-4 py-1.5 rounded-md text-sm transition-colors ${view === "2d" ? "bg-indigo-600 text-white shadow" : "text-slate-400 hover:text-white"}`}
            >
            Isole (2D)
          </button>
          <button
            onClick={() => setView("3d")}
            className={`px-4 py-1.5 rounded-md text-sm transition-colors ${view === "3d" ? "bg-indigo-600 text-white shadow" : "text-slate-400 hover:text-white"}`}
          >
            Galassia (3D)
          </button>
          <button
            onClick={() => setView("graph")}
            className={`px-4 py-1.5 rounded-md text-sm transition-colors ${view === "graph" ? "bg-indigo-600 text-white shadow" : "text-slate-400 hover:text-white"}`}
          >
            Rete Neurale
          </button>
        </div>
        </div>
      </div>

      <div className="flex-1 w-full h-full min-h-[500px] bg-slate-950 rounded-xl border border-slate-800 overflow-hidden relative shadow-2xl flex items-center justify-center">
        {/* VISTA 1: t-SNE 2D */}
        {view === "2d" && (
          <Plot
            data={plotly2D}
            layout={{
              ...plotLayout,
              xaxis: { visible: false },
              yaxis: { visible: false },
            }}
            useResizeHandler={true}
            style={{ width: "100%", height: "100%", minHeight: "500px" }}
            config={{ displayModeBar: false }}
          />
        )}

        {/* VISTA 2: PCA 3D */}
        {view === "3d" && (
          <Plot
            data={plotly3D}
            layout={{
              ...plotLayout,
              scene: {
                xaxis: {
                  color: "#64748b",
                  gridcolor: "#1e293b",
                  zerolinecolor: "#334155",
                  backgroundcolor: "rgba(0,0,0,0)",
                },
                yaxis: {
                  color: "#64748b",
                  gridcolor: "#1e293b",
                  zerolinecolor: "#334155",
                  backgroundcolor: "rgba(0,0,0,0)",
                },
                zaxis: {
                  color: "#64748b",
                  gridcolor: "#1e293b",
                  zerolinecolor: "#334155",
                  backgroundcolor: "rgba(0,0,0,0)",
                },
                bgcolor: "rgba(0,0,0,0)",
              },
            }}
            useResizeHandler={true}
            style={{ width: "100%", height: "100%", minHeight: "500px" }}
            config={{ displayModeBar: false }}
          />
        )}

        {/* VISTA 3: KNOWLEDGE GRAPH */}
        {view === "graph" && (
          <ForceGraph2D
            graphData={mapData.graph}
            nodeLabel="preview"
            nodeAutoColorBy="name"
            linkColor={() => "rgba(99, 102, 241, 0.4)"}
            linkWidth={1.5}
            backgroundColor="#020617" // slate-950
            width={800} // Verrà sovrascritto se aggiungiamo un resize observer, ma va bene come fallback
            height={600}
          />
        )}
      </div>
    </div>
  );
}

// 3. Pagina Esplora Vault (NUOVA)
function VaultPage() {
  const [vaultData, setVaultData] = useState<{
    documents: any[];
    total: number;
  }>({ documents: [], total: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/vault`)
      .then((res) => res.json())
      .then((data) => setVaultData(data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="flex-1 flex flex-col max-w-5xl mx-auto w-full p-6 h-full">
      <header className="mb-6">
        <h2 className="text-2xl font-semibold opacity-80">Esplora Database</h2>
        <p className="text-slate-400 mt-1">
          {loading
            ? "Lettura DB in corso..."
            : `Totale frammenti (chunks) vettorializzati: ${vaultData.total}`}
        </p>
      </header>

      {vaultData.total === 0 && !loading ? (
        <div className="flex-1 flex flex-col items-center justify-center border-2 border-dashed border-slate-700 rounded-xl opacity-50">
          <Database size={48} className="mb-4" />
          <p>Il Database è vuoto. Processa alcune note per iniziare.</p>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto grid grid-cols-1 md:grid-cols-2 gap-4 auto-rows-max pr-2">
          {vaultData.documents.map((doc, idx) => (
            <div
              key={idx}
              className="bg-slate-800/50 border border-slate-700 p-4 rounded-xl flex flex-col"
            >
              <div className="text-xs font-bold text-indigo-400 mb-2 uppercase tracking-wider">
                {doc.source}
              </div>
              <div className="text-sm text-slate-300 italic">
                "{doc.preview}"
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// 4. Pagina Editor
function EditorPage() {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [status, setStatus] = useState<"idle" | "saving" | "saved" | "error">(
    "idle",
  );

  const [isAiPanelOpen, setIsAiPanelOpen] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiResult, setAiResult] = useState("");
  const [aiActionType, setAiActionType] = useState("");

  const [showSlashMenu, setShowSlashMenu] = useState(false);
  const [slashQuery, setSlashQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);
  
  const [viewMode, setViewMode] = useState<"edit" | "preview" | "split">("edit");

  // Filtra i comandi in base a quello che scrivi dopo lo slash (es: /h1)
  const filteredCommands = SLASH_COMMANDS.filter(
    (cmd) =>
      cmd.id.includes(slashQuery.toLowerCase()) ||
      cmd.label.toLowerCase().includes(slashQuery.toLowerCase()),
  );

  const executeCommand = async (cmd: any) => {
    // Rimuoviamo lo slash inserito
    const lastSlashIndex = content.lastIndexOf("/");
    const newContent = content.substring(0, lastSlashIndex);
    setContent(newContent);
    setShowSlashMenu(false);
    setSlashQuery("");

    if (!cmd.type || cmd.type === "format") {
      setContent(newContent + cmd.syntax);
      setIsTyping(true);
    } else if (cmd.type === "ai") {
      // LOGICA AI
      setIsAiPanelOpen(true);
      setAiLoading(true);
      setAiResult("");
      setAiActionType(cmd.label);

      // Prendi il testo selezionato, oppure l'intero contenuto
      const textarea = document.getElementById(
        "main-editor",
      ) as HTMLTextAreaElement;
      let targetText = newContent;

      // Se c'era del testo selezionato prima dello slash (un po' trick, ma proviamo)
      if (textarea && textarea.selectionStart !== textarea.selectionEnd) {
        targetText = textarea.value.substring(
          textarea.selectionStart,
          textarea.selectionEnd,
        );
      }

      try {
        const res = await fetch(`${API_URL}/editor/ai`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: targetText, action: cmd.syntax }),
        });
        if (!res.ok) throw new Error("Errore durante l'analisi AI");
        const data = await res.json();
        setAiResult(data.result);
      } catch (error: any) {
        setAiResult(`❌ Errore: ${error.message}`);
      } finally {
        setAiLoading(false);
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (showSlashMenu) {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIndex((prev) => (prev + 1) % filteredCommands.length);
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIndex(
          (prev) =>
            (prev - 1 + filteredCommands.length) % filteredCommands.length,
        );
      } else if (e.key === "Enter") {
        e.preventDefault();
        executeCommand(filteredCommands[selectedIndex]); // <--- Aggiornato qui
      } else if (e.key === "Escape") {
        setShowSlashMenu(false);
      }
    }
  };

  // Nuovi stati per il caricamento delle note
  const [availableNotes, setAvailableNotes] = useState<string[]>([]);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isTyping, setIsTyping] = useState(false);

  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const val = e.target.value;
    setContent(val);
    setIsTyping(true);

    // Logica per mostrare il menu: se l'ultimo carattere o la parola corrente inizia con /
    const words = val.split(/(\s+)/);
    const lastWord = words[words.length - 1];

    if (lastWord.startsWith("/")) {
      setShowSlashMenu(true);
      setSlashQuery(lastWord.substring(1)); // Prende tutto dopo lo slash per filtrare
      setSelectedIndex(0);
    } else {
      setShowSlashMenu(false);
    }
  };

  // 4. Gestione Drag & Drop Immagini/File
  const handleDragOver = (e: React.DragEvent<HTMLTextAreaElement>) => {
    e.preventDefault();
  };

  const handleDrop = async (e: React.DragEvent<HTMLTextAreaElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      // Controlla se è un file o un'immagine supportata
      const formData = new FormData();
      formData.append("file", file);

      setStatus("saving");

      try {
        const res = await fetch(`${API_URL}/upload`, {
          method: "POST",
          body: formData,
        });

        if (res.ok) {
          const data = await res.json();
          const textarea = e.target as HTMLTextAreaElement;
          const cursorPos = textarea.selectionStart ?? content.length;

          const textBefore = content.substring(0, cursorPos);
          const textAfter = content.substring(cursorPos);

          const newContent = textBefore + data.markdown_syntax + textAfter;
          setContent(newContent);
          setIsTyping(true);
          setStatus("saved");
        } else {
          setStatus("error");
        }
      } catch (err) {
        setStatus("error");
      }
    }
  };

  // 1. Carica la lista delle note all'apertura dell'editor
  useEffect(() => {
    fetch(`${API_URL}/notes`)
      .then((res) => res.json())
      .then((data) => setAvailableNotes(data.notes || []))
      .catch(console.error);
  }, [status]); // Ricarica la lista ogni volta che salviamo una nuova nota

  // Parse degli allegati (assets/) dal contenuto testuale
  const attachments = Array.from(content.matchAll(/(!?)\[([^\]]*)\]\((assets\/([^)]+))\)/g)).map(match => ({
    fullMatch: match[0],
    isImage: match[1] === "!",
    label: match[2],
    path: match[3],
    filename: match[4]
  }));

  const deleteAttachment = async (fullMatch: string, filename: string) => {
    setStatus("saving");
    try {
      const res = await fetch(`${API_URL}/upload/${filename}`, {
        method: "DELETE"
      });
      if (res.ok) {
        // Rimuove la sintassi markdown dal blocco di testo
        const newContent = content.replace(fullMatch, "");
        setContent(newContent);
        setIsTyping(true);
        setStatus("saved");
      } else {
        setStatus("error");
      }
    } catch (err) {
      setStatus("error");
    }
  };

  // 2. Funzione per caricare una nota specifica
  const loadNote = async (filename: string) => {
    try {
      const res = await fetch(`${API_URL}/notes/${filename}`);
      if (!res.ok) throw new Error("Errore nel caricamento della nota");
      const data = await res.json();

      // Blocca l'auto-save temporaneamente per evitare sovrascritture accidentali al caricamento
      setIsTyping(false);
      setTitle(data.title);
      setContent(data.content);
      setIsMenuOpen(false);
      setStatus("idle");
    } catch (err) {
      console.error(err);
      setStatus("error");
    }
  };

  // 3. LOGICA DI AUTO-SALVATAGGIO aggiornata
  useEffect(() => {
    if (!isTyping) return; // Non salvare se abbiamo appena caricato un file
    if (!title.trim() && !content.trim()) return;

    const timer = setTimeout(() => {
      autoSave();
    }, 2000);

    return () => clearTimeout(timer);
  }, [title, content, isTyping]);

  const autoSave = async () => {
    setStatus("saving");
    try {
      const res = await fetch(`${API_URL}/notes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: title || "Senza Titolo", content }),
      });

      if (res.ok) {
        setStatus("saved");
        setTimeout(() => setStatus("idle"), 2000);
      } else {
        setStatus("error");
      }
    } catch (err) {
      setStatus("error");
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-slate-950 text-slate-200">
      {/* TOOLBAR SUPERIORE */}
      <div className="flex justify-between items-center p-4 border-b border-slate-800/50">
        {/* MENU APRI NOTA */}
        <div className="relative">
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm text-slate-300 transition-colors border border-slate-700"
          >
            <FolderOpen size={16} /> Apri Nota
          </button>

          {isMenuOpen && (
            <div className="absolute top-full left-0 mt-2 w-64 bg-slate-800 border border-slate-700 rounded-lg shadow-xl z-50 max-h-64 overflow-y-auto">
              {availableNotes.length === 0 ? (
                <div className="p-3 text-sm text-slate-500">
                  Nessuna nota in raw_notes/
                </div>
              ) : (
                availableNotes.map((note) => (
                  <button
                    key={note}
                    onClick={() => loadNote(note)}
                    className="w-full text-left px-4 py-2 text-sm text-slate-300 hover:bg-indigo-600 hover:text-white transition-colors"
                  >
                    {note}
                  </button>
                ))
              )}
            </div>
          )}
        </div>

        {/* STATO SALVATAGGIO */}
        <div className="flex items-center gap-2 text-sm font-medium">
          <div
            className={`w-2 h-2 rounded-full ${
              status === "saving"
                ? "bg-amber-500 animate-ping"
                : status === "saved"
                  ? "bg-emerald-500"
                  : "bg-slate-700"
            }`}
          />
          {status === "saving" && (
            <span className="text-slate-400">Salvataggio in corso...</span>
          )}
          {status === "saved" && (
            <span className="text-emerald-400">
              Tutte le modifiche salvate in Raw Notes
            </span>
          )}
          {status === "idle" && (
            <span className="text-slate-500">Pronto in raw_notes/</span>
          )}
          {status === "error" && (
            <span className="text-red-400">Errore di connessione</span>
          )}
        </div>
      </div>

      {/* CONTENITORE PRINCIPALE DIVISO A METÀ */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* AREA EDITOR */}
        <div
          className={`flex-1 overflow-y-auto px-6 py-12 md:px-24 transition-all duration-300 ${isAiPanelOpen ? "lg:px-12" : "lg:px-48"}`}
        >
          <div className="max-w-7xl mx-auto flex flex-col h-full gap-6 relative">
            {/* TITOLO E CONTROLLI LAYOUT */}
            <div className="flex items-center justify-between gap-6">
              <input
                type="text"
                value={title}
                onChange={(e) => {
                  setTitle(e.target.value);
                  setIsTyping(true);
                }}
                placeholder="Titolo della nota"
                className="flex-1 bg-transparent text-4xl font-bold text-slate-100 placeholder-slate-700 outline-none border-none focus:ring-0"
              />

              <div className="flex bg-slate-800 p-1.5 rounded-lg border border-slate-700 shadow-sm z-10 shrink-0">
                <button 
                  onClick={() => setViewMode("edit")} 
                  className={`p-2 rounded-md transition-colors ${viewMode === "edit" ? "bg-indigo-600 text-white shadow-md text-xs" : "text-slate-400 hover:text-slate-200"}`}
                  title="Editor testuale"
                >
                  <Edit3 size={18} />
                </button>
                <button 
                  onClick={() => setViewMode("split")} 
                  className={`p-2 rounded-md transition-colors mx-1 ${viewMode === "split" ? "bg-indigo-600 text-white shadow-md text-xs" : "text-slate-400 hover:text-slate-200"}`}
                  title="Vista Ripartita"
                >
                  <Columns size={18} />
                </button>
                <button 
                  onClick={() => setViewMode("preview")} 
                  className={`p-2 rounded-md transition-colors ${viewMode === "preview" ? "bg-indigo-600 text-white shadow-md text-xs" : "text-slate-400 hover:text-slate-200"}`}
                  title="Solo Lettura"
                >
                  <Eye size={18} />
                </button>
              </div>
            </div>

            {/* AREA CONTENUTO MULTI-VISTA */}
            <div className="relative flex-1 flex flex-col lg:flex-row gap-8 overflow-hidden pb-6">

              {/* PANNELLO TEXTAREA */}
              {(viewMode === "edit" || viewMode === "split") && (
                <div className={`relative flex-1 flex flex-col group h-full ${viewMode === "split" ? "lg:border-r lg:border-slate-800 lg:pr-8" : ""}`}>
                  <textarea
                    id="main-editor"
                    value={content}
                    onChange={handleContentChange}
                    onKeyDown={handleKeyDown}
                    onDragOver={handleDragOver}
                    onDrop={handleDrop}
                placeholder="Scrivi qui..."
                className="w-full flex-1 bg-transparent text-lg text-slate-300 placeholder-slate-700 outline-none border-none focus:ring-0 resize-none leading-relaxed transition-colors border-2 border-dashed border-transparent hover:border-slate-800 rounded-xl"
              />

              {/* LISTA ALLEGATI CARICATI */}
              {attachments.length > 0 && (
                <div className="absolute bottom-4 left-4 right-4 bg-slate-900/80 backdrop-blur-md border border-slate-700 rounded-xl p-3 flex gap-4 overflow-x-auto shadow-2xl z-40">
                  <div className="flex items-center text-xs font-semibold text-slate-500 uppercase tracking-wider pl-2 pr-4 border-r border-slate-700/50">
                    Allegati
                  </div>
                  {attachments.map((att, idx) => (
                    <div key={idx} className="flex items-stretch bg-slate-800 rounded-lg overflow-hidden border border-slate-700 group hover:border-indigo-500/50 transition-colors flex-shrink-0">
                      {/* PREVIEW SE IMMAGINE, ICONA SE PDF */}
                      <a href={`${ASSETS_URL}/${att.filename}`} target="_blank" rel="noopener noreferrer" className="p-2 bg-slate-900 flex items-center justify-center min-w-[3rem] hover:bg-slate-700 transition-colors">
                        {att.isImage ? (
                          <img src={`${ASSETS_URL}/${att.filename}`} alt={att.label} className="w-8 h-8 object-cover rounded shadow ring-1 ring-slate-800" />
                        ) : (
                          <FileText size={20} className="text-slate-400" />
                        )}
                      </a>
                      
                      <div className="flex flex-col justify-center px-3 py-1 flex-1">
                        <div className="text-xs font-medium text-slate-300 max-w-[120px] truncate" title={att.filename}>
                          {att.filename}
                        </div>
                        <div className="text-[10px] text-slate-500 uppercase">
                          {att.isImage ? "Immagine" : "Documento"}
                        </div>
                      </div>

                      <button 
                        onClick={() => deleteAttachment(att.fullMatch, att.filename)}
                        title="Elimina"
                        className="px-3 flex items-center justify-center bg-red-950/30 text-red-400 hover:bg-red-600 hover:text-white transition-colors border-l border-slate-700"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  ))}
                </div>
              )}

              {showSlashMenu && filteredCommands.length > 0 && (
                <div className="absolute top-10 left-0 w-64 bg-slate-900 border border-slate-700 rounded-xl shadow-2xl z-[100] overflow-hidden">
                  <div className="p-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Comandi & AI
                  </div>
                  {filteredCommands.map((cmd, index) => (
                    <div
                      key={cmd.id}
                      onClick={() => executeCommand(cmd)}
                      className={`flex items-center gap-3 px-4 py-2 cursor-pointer transition-colors ${
                        index === selectedIndex
                          ? "bg-indigo-600 text-white"
                          : "hover:bg-slate-800 text-slate-300"
                      }`}
                    >
                      <span
                        className={`w-6 h-6 flex items-center justify-center rounded text-xs font-bold ${cmd.type === "ai" ? "bg-indigo-500/20 text-indigo-300" : "bg-slate-800"}`}
                      >
                        {cmd.icon}
                      </span>
                      <span className="text-sm font-medium">{cmd.label}</span>
                    </div>
                  ))}
                </div>
              )}
                </div>
              )}

              {/* PANNELLO ANTEPRIMA (RENDER MARKDOWN + IMMAGINI GRANDI) ESEGUITO SOLO IN SPLIT O PREVIEW */}
              {(viewMode === "preview" || viewMode === "split") && (
                <div className={`overflow-y-auto h-full pr-4 pb-20 prose prose-invert prose-indigo prose-p:leading-relaxed prose-pre:bg-slate-950 prose-pre:border prose-pre:border-slate-800 prose-img:rounded-xl prose-img:max-w-full max-w-none ${viewMode === "split" ? "w-1/2" : "w-full"}`}>
                  {content.trim() ? (
                    <ReactMarkdown
                      components={{
                        img: ({node, src, alt, ...props}) => {
                          const imgSrc = src?.startsWith('assets/') ? `${ASSETS_URL}/${src.split('assets/')[1]}` : src;
                          return <img src={imgSrc} alt={alt || ''} {...props} className="my-6 shadow-xl border border-slate-800 object-contain w-auto max-h-[60vh] bg-slate-900 rounded-xl" />;
                        },
                        a: ({node, href, children, ...props}) => {
                          const linkHref = href?.startsWith('assets/') ? `${ASSETS_URL}/${href.split('assets/')[1]}` : href;
                          return <a href={linkHref} target="_blank" rel="noopener noreferrer" className="text-indigo-400 hover:text-indigo-300 transition-colors underline" {...props}>{children}</a>;
                        }
                      }}
                    >
                      {content}
                    </ReactMarkdown>
                  ) : (
                    <div className="flex items-center justify-center h-full text-slate-600 italic">
                      Anteprima... Appariranno qui i tuoi contenuti.
                    </div>
                  )}
                </div>
              )}

            </div>
          </div>
        </div>

        {/* PANNELLO LATERALE AI */}
        {isAiPanelOpen && (
          <div className="w-96 border-l border-slate-800 bg-slate-900/50 flex flex-col shadow-2xl animate-in slide-in-from-right">
            {/* Header Pannello */}
            <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-900">
              <div className="flex items-center gap-2 text-indigo-400 font-medium">
                <Sparkles size={16} />
                {aiActionType}
              </div>
              <button
                onClick={() => setIsAiPanelOpen(false)}
                className="text-slate-400 hover:text-white p-1 rounded-md hover:bg-slate-800 transition-colors"
              >
                <X size={18} />
              </button>
            </div>

            {/* Contenuto Pannello */}
            <div className="flex-1 overflow-y-auto p-6 scrollbar-hide">
              {aiLoading ? (
                <div className="flex flex-col items-center justify-center h-full text-slate-500 gap-4">
                  <Wand2 size={32} className="animate-pulse text-indigo-500" />
                  <p className="text-sm text-center animate-pulse">
                    Sto analizzando i tuoi appunti e <br />
                    {aiActionType === "Valida Fonti"
                      ? "verificando sul web"
                      : "cercando collegamenti"}
                    ...
                  </p>
                </div>
              ) : (
                <div className="prose prose-invert prose-sm prose-indigo prose-p:leading-relaxed prose-pre:bg-slate-950 prose-pre:border prose-pre:border-slate-800 prose-img:rounded-lg prose-img:max-w-full max-w-none">
                  <ReactMarkdown
                    components={{
                      img: ({node, src, alt, ...props}) => {
                        const imgSrc = src?.startsWith('assets/') ? `${ASSETS_URL}/${src.split('assets/')[1]}` : src;
                        return <img src={imgSrc} alt={alt || ''} {...props} className="my-2" />;
                      }
                    }}
                  >{aiResult}</ReactMarkdown>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// --- LAYOUT & ROUTING ---
function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const [actionStatus, setActionStatus] = useState<string | null>(null);

  const triggerAction = async (endpoint: string, msg: string) => {
    setActionStatus("Esecuzione in corso...");
    try {
      const res = await fetch(`${API_URL}/${endpoint}`, { method: "POST" });
      const data = await res.json();
      setActionStatus(data.message || msg);
    } catch (err: any) {
      setActionStatus("❌ Errore");
    }
    setTimeout(() => setActionStatus(null), 4000);
  };

  const navClass = (path: string) =>
    `flex items-center gap-3 p-3 rounded-lg transition-colors ${location.pathname === path ? "bg-indigo-600/20 text-indigo-400 border border-indigo-500/30" : "hover:bg-slate-800 text-slate-300"}`;

  return (
    <div className="flex h-screen bg-slate-900 text-slate-100 font-sans overflow-hidden">
      <div className="w-64 bg-slate-950 p-4 flex flex-col border-r border-slate-800 flex-shrink-0">
        <h1 className="text-xl font-bold mb-8 text-center text-indigo-400">
          🧠 Second Brain
        </h1>
        <nav className="flex flex-col gap-2 mb-10">
          <Link to="/" className={navClass("/")}>
            <MessageSquare size={18} /> Chat RAG
          </Link>
          <Link to="/map" className={navClass("/map")}>
            <MapIcon size={18} /> Mappa 3D
          </Link>
          <Link to="/vault" className={navClass("/vault")}>
            <Database size={18} /> Esplora DB
          </Link>
          <Link to="/editor" className={navClass("/editor")}>
            <PenTool size={18} /> Scrivi Nota
          </Link>
        </nav>
        <div className="mt-auto flex flex-col gap-3 border-t border-slate-800 pt-6">
          <button
            onClick={() => triggerAction("process", "Processo Inbox terminato")}
            className="flex items-center justify-center gap-2 bg-slate-800 hover:bg-slate-700 p-3 rounded-lg border border-slate-700 text-sm"
          >
            <FolderSync size={16} className="text-amber-400" /> Processa Inbox
          </button>
          <button
            onClick={() => triggerAction("sync", "Sync terminata")}
            className="flex items-center justify-center gap-2 bg-slate-800 hover:bg-slate-700 p-3 rounded-lg border border-slate-700 text-sm"
          >
            <RefreshCw size={16} className="text-emerald-400" /> Sync Database
          </button>
        </div>
        {actionStatus && (
          <div className="mt-4 bg-slate-800 text-xs p-3 rounded text-amber-200 border border-amber-900 text-center">
            {actionStatus}
          </div>
        )}
      </div>
      <main className="flex-1 flex overflow-hidden">{children}</main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<ChatPage />} />
          <Route path="/map" element={<MapPage />} />
          <Route path="/vault" element={<VaultPage />} />
          <Route path="/editor" element={<EditorPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
