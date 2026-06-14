import { useState, useEffect } from "react";
import { API_URL } from "../lib/config";
import type { Attachment, SaveStatus, SlashCommand, ViewMode } from "../types";
import { SLASH_COMMANDS } from "../constants/slashCommands";
import Markdown from "../components/Markdown";
import NotePicker from "../components/editor/NotePicker";
import SaveStatusIndicator from "../components/editor/SaveStatus";
import ViewModeToggle from "../components/editor/ViewModeToggle";
import SlashMenu from "../components/editor/SlashMenu";
import AttachmentBar from "../components/editor/AttachmentBar";
import AiPanel from "../components/editor/AiPanel";

const PREVIEW_IMG_CLASS =
  "my-6 shadow-xl border border-slate-800 object-contain w-auto max-h-[60vh] bg-slate-900 rounded-xl";

// Markdown note editor: live preview, "/" command palette, AI copilot,
// drag-and-drop uploads and debounced auto-save to raw_notes/.
export default function EditorPage() {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [status, setStatus] = useState<SaveStatus>("idle");

  const [isAiPanelOpen, setIsAiPanelOpen] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiResult, setAiResult] = useState("");
  const [aiActionType, setAiActionType] = useState("");

  const [showSlashMenu, setShowSlashMenu] = useState(false);
  const [slashQuery, setSlashQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [viewMode, setViewMode] = useState<ViewMode>("edit");

  const [availableNotes, setAvailableNotes] = useState<string[]>([]);
  const [isTyping, setIsTyping] = useState(false);

  // Filter the commands based on what you type after the slash (e.g.: /h1)
  const filteredCommands = SLASH_COMMANDS.filter(
    (cmd) =>
      cmd.id.includes(slashQuery.toLowerCase()) ||
      cmd.label.toLowerCase().includes(slashQuery.toLowerCase()),
  );

  const executeCommand = async (cmd: SlashCommand) => {
    // Remove the inserted slash
    const lastSlashIndex = content.lastIndexOf("/");
    const newContent = content.substring(0, lastSlashIndex);
    setContent(newContent);
    setShowSlashMenu(false);
    setSlashQuery("");

    if (!cmd.type || cmd.type === "format") {
      setContent(newContent + cmd.syntax);
      setIsTyping(true);
    } else if (cmd.type === "ai") {
      setIsAiPanelOpen(true);
      setAiLoading(true);
      setAiResult("");
      setAiActionType(cmd.label);

      // Take the selected text, or the entire content
      const textarea = document.getElementById("main-editor") as HTMLTextAreaElement;
      let targetText = newContent;
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
        if (!res.ok) throw new Error("Error during AI analysis");
        const data = await res.json();
        setAiResult(data.result);
      } catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        setAiResult(`❌ Error: ${message}`);
      } finally {
        setAiLoading(false);
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!showSlashMenu) return;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSelectedIndex((prev) => (prev + 1) % filteredCommands.length);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSelectedIndex(
        (prev) => (prev - 1 + filteredCommands.length) % filteredCommands.length,
      );
    } else if (e.key === "Enter") {
      e.preventDefault();
      executeCommand(filteredCommands[selectedIndex]);
    } else if (e.key === "Escape") {
      setShowSlashMenu(false);
    }
  };

  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const val = e.target.value;
    setContent(val);
    setIsTyping(true);

    // Show the menu if the current word starts with /
    const words = val.split(/(\s+)/);
    const lastWord = words[words.length - 1];
    if (lastWord.startsWith("/")) {
      setShowSlashMenu(true);
      setSlashQuery(lastWord.substring(1));
      setSelectedIndex(0);
    } else {
      setShowSlashMenu(false);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLTextAreaElement>) => {
    e.preventDefault();
  };

  const handleDrop = async (e: React.DragEvent<HTMLTextAreaElement>) => {
    e.preventDefault();
    if (!e.dataTransfer.files || e.dataTransfer.files.length === 0) return;

    const file = e.dataTransfer.files[0];
    const formData = new FormData();
    formData.append("file", file);
    setStatus("saving");

    try {
      const res = await fetch(`${API_URL}/upload`, { method: "POST", body: formData });
      if (res.ok) {
        const data = await res.json();
        const textarea = e.target as HTMLTextAreaElement;
        const cursorPos = textarea.selectionStart ?? content.length;
        const newContent =
          content.substring(0, cursorPos) +
          data.markdown_syntax +
          content.substring(cursorPos);
        setContent(newContent);
        setIsTyping(true);
        setStatus("saved");
      } else {
        setStatus("error");
      }
    } catch {
      setStatus("error");
    }
  };

  // Reload the list of available notes (re-runs whenever a note is saved)
  useEffect(() => {
    fetch(`${API_URL}/notes`)
      .then((res) => res.json())
      .then((data) => setAvailableNotes(data.notes || []))
      .catch(console.error);
  }, [status]);

  // Parse the attachments (assets/) from the text content
  const attachments: Attachment[] = Array.from(
    content.matchAll(/(!?)\[([^\]]*)\]\((assets\/([^)]+))\)/g),
  ).map((match) => ({
    fullMatch: match[0],
    isImage: match[1] === "!",
    label: match[2],
    path: match[3],
    filename: match[4],
  }));

  const deleteAttachment = async (fullMatch: string, filename: string) => {
    setStatus("saving");
    try {
      const res = await fetch(`${API_URL}/upload/${filename}`, { method: "DELETE" });
      if (res.ok) {
        setContent(content.replace(fullMatch, ""));
        setIsTyping(true);
        setStatus("saved");
      } else {
        setStatus("error");
      }
    } catch {
      setStatus("error");
    }
  };

  const loadNote = async (filename: string) => {
    try {
      const res = await fetch(`${API_URL}/notes/${filename}`);
      if (!res.ok) throw new Error("Error loading the note");
      const data = await res.json();
      // Block auto-save momentarily to avoid overwriting on load
      setIsTyping(false);
      setTitle(data.title);
      setContent(data.content);
      setStatus("idle");
    } catch (err) {
      console.error(err);
      setStatus("error");
    }
  };

  // Debounced auto-save
  useEffect(() => {
    if (!isTyping) return;
    if (!title.trim() && !content.trim()) return;

    const timer = setTimeout(async () => {
      setStatus("saving");
      try {
        const res = await fetch(`${API_URL}/notes`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ title: title || "Untitled", content }),
        });
        if (res.ok) {
          setStatus("saved");
          setTimeout(() => setStatus("idle"), 2000);
        } else {
          setStatus("error");
        }
      } catch {
        setStatus("error");
      }
    }, 2000);

    return () => clearTimeout(timer);
  }, [title, content, isTyping]);

  const showEditor = viewMode === "edit" || viewMode === "split";
  const showPreview = viewMode === "preview" || viewMode === "split";

  return (
    <div className="flex-1 flex flex-col h-full bg-slate-950 text-slate-200">
      {/* TOP TOOLBAR */}
      <div className="flex justify-between items-center p-4 border-b border-slate-800/50">
        <NotePicker notes={availableNotes} onSelect={loadNote} />
        <SaveStatusIndicator status={status} />
      </div>

      {/* MAIN CONTAINER */}
      <div className="flex-1 flex overflow-hidden relative">
        <div
          className={`flex-1 overflow-y-auto px-6 py-12 md:px-24 transition-all duration-300 ${
            isAiPanelOpen ? "lg:px-12" : "lg:px-48"
          }`}
        >
          <div className="max-w-7xl mx-auto flex flex-col h-full gap-6 relative">
            {/* TITLE AND LAYOUT CONTROLS */}
            <div className="flex items-center justify-between gap-6">
              <input
                type="text"
                value={title}
                onChange={(e) => {
                  setTitle(e.target.value);
                  setIsTyping(true);
                }}
                placeholder="Note title"
                className="flex-1 bg-transparent text-4xl font-bold text-slate-100 placeholder-slate-700 outline-none border-none focus:ring-0"
              />
              <ViewModeToggle viewMode={viewMode} setViewMode={setViewMode} />
            </div>

            {/* MULTI-VIEW CONTENT AREA */}
            <div className="relative flex-1 flex flex-col lg:flex-row gap-8 overflow-hidden pb-6">
              {showEditor && (
                <div
                  className={`relative flex-1 flex flex-col group h-full ${
                    viewMode === "split" ? "lg:border-r lg:border-slate-800 lg:pr-8" : ""
                  }`}
                >
                  <textarea
                    id="main-editor"
                    value={content}
                    onChange={handleContentChange}
                    onKeyDown={handleKeyDown}
                    onDragOver={handleDragOver}
                    onDrop={handleDrop}
                    placeholder="Write here..."
                    className="w-full flex-1 bg-transparent text-lg text-slate-300 placeholder-slate-700 outline-none border-none focus:ring-0 resize-none leading-relaxed transition-colors border-2 border-dashed border-transparent hover:border-slate-800 rounded-xl"
                  />

                  {attachments.length > 0 && (
                    <AttachmentBar attachments={attachments} onDelete={deleteAttachment} />
                  )}

                  {showSlashMenu && filteredCommands.length > 0 && (
                    <SlashMenu
                      commands={filteredCommands}
                      selectedIndex={selectedIndex}
                      onSelect={executeCommand}
                    />
                  )}
                </div>
              )}

              {showPreview && (
                <div
                  className={`overflow-y-auto h-full pr-4 pb-20 prose prose-invert prose-indigo prose-p:leading-relaxed prose-pre:bg-slate-950 prose-pre:border prose-pre:border-slate-800 prose-img:rounded-xl prose-img:max-w-full max-w-none ${
                    viewMode === "split" ? "w-1/2" : "w-full"
                  }`}
                >
                  {content.trim() ? (
                    <Markdown content={content} imgClassName={PREVIEW_IMG_CLASS} />
                  ) : (
                    <div className="flex items-center justify-center h-full text-slate-600 italic">
                      Preview... Your content will appear here.
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {isAiPanelOpen && (
          <AiPanel
            actionType={aiActionType}
            loading={aiLoading}
            result={aiResult}
            onClose={() => setIsAiPanelOpen(false)}
          />
        )}
      </div>
    </div>
  );
}
