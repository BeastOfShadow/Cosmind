import { Sparkles, X, Wand2 } from "lucide-react";
import Markdown from "../Markdown";

interface AiPanelProps {
  actionType: string;
  loading: boolean;
  result: string;
  onClose: () => void;
}

// Side panel showing the editor copilot's output (expand / validate / tutor).
export default function AiPanel({ actionType, loading, result, onClose }: AiPanelProps) {
  return (
    <div className="w-96 border-l border-slate-800 bg-slate-900/50 flex flex-col shadow-2xl animate-in slide-in-from-right">
      <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-900">
        <div className="flex items-center gap-2 text-indigo-400 font-medium">
          <Sparkles size={16} />
          {actionType}
        </div>
        <button
          onClick={onClose}
          className="text-slate-400 hover:text-white p-1 rounded-md hover:bg-slate-800 transition-colors"
        >
          <X size={18} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-6 scrollbar-hide">
        {loading ? (
          <div className="flex flex-col items-center justify-center h-full text-slate-500 gap-4">
            <Wand2 size={32} className="animate-pulse text-indigo-500" />
            <p className="text-sm text-center animate-pulse">
              Analyzing your notes and <br />
              {actionType === "Validate Sources"
                ? "verifying on the web"
                : "looking for connections"}
              ...
            </p>
          </div>
        ) : (
          <div className="prose prose-invert prose-sm prose-indigo prose-p:leading-relaxed prose-pre:bg-slate-950 prose-pre:border prose-pre:border-slate-800 prose-img:rounded-lg prose-img:max-w-full max-w-none">
            <Markdown content={result} imgClassName="my-2" />
          </div>
        )}
      </div>
    </div>
  );
}
