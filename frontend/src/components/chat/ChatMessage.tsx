import { Bot, User } from "lucide-react";
import type { ChatMessage as ChatMessageType } from "../../types";
import Markdown from "../Markdown";
import SourceList from "./SourceList";

// A single chat bubble (user or bot). Bot messages render markdown + sources.
export default function ChatMessage({ msg }: { msg: ChatMessageType }) {
  const isBot = msg.role === "bot";
  return (
    <div className={`flex gap-4 ${isBot ? "justify-start" : "justify-end"}`}>
      {isBot && (
        <div className="w-8 h-8 rounded-full bg-indigo-600/20 flex items-center justify-center border border-indigo-500/30 flex-shrink-0 mt-1">
          <Bot size={18} className="text-indigo-400" />
        </div>
      )}

      <div
        className={`max-w-[85%] rounded-2xl p-4 ${
          isBot
            ? "bg-slate-800 text-slate-200 rounded-tl-sm border border-slate-700/50 shadow-sm"
            : "bg-indigo-600 text-white rounded-tr-sm"
        }`}
      >
        {isBot ? (
          <div className="prose prose-invert prose-p:leading-relaxed prose-pre:bg-slate-900 prose-pre:border prose-pre:border-slate-700 prose-img:rounded-xl prose-img:max-w-full max-w-none">
            <Markdown content={msg.content} imgClassName="my-4" />
          </div>
        ) : (
          <div className="leading-relaxed whitespace-pre-wrap">{msg.content}</div>
        )}

        {isBot && msg.sources && msg.sources.length > 0 && (
          <SourceList sources={msg.sources} />
        )}
      </div>

      {!isBot && (
        <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center flex-shrink-0 mt-1">
          <User size={18} className="text-slate-300" />
        </div>
      )}
    </div>
  );
}
