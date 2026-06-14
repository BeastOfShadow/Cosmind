import { useState } from "react";
import { Send, Bot } from "lucide-react";
import { API_URL } from "../lib/config";
import type { ChatMessage as ChatMessageType } from "../types";
import ChatMessage from "../components/chat/ChatMessage";

// RAG chat: ask a question, get an answer grounded only in the vault notes.
export default function ChatPage() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
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
      if (!res.ok) throw new Error(`HTTP Error: ${res.status}`);
      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { role: "bot", content: data.answer, sources: data.sources },
      ]);
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      setMessages((prev) => [...prev, { role: "bot", content: `Error: ${message}` }]);
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
              Ask Cosmind a question.
              <br />
              <span className="text-sm">It will answer using only your notes.</span>
            </p>
          </div>
        )}

        {messages.map((msg, i) => (
          <ChatMessage key={i} msg={msg} />
        ))}

        {loading && (
          <div className="flex gap-4 justify-start animate-pulse">
            <div className="w-8 h-8 rounded-full bg-indigo-600/20 flex items-center justify-center border border-indigo-500/30">
              <Bot size={18} className="text-indigo-400" />
            </div>
            <div className="bg-slate-800 rounded-2xl rounded-tl-sm p-4 text-slate-400 border border-slate-700/50">
              Searching the Vault...
            </div>
          </div>
        )}
      </div>

      <form onSubmit={askBrain} className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask something about your notes..."
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
