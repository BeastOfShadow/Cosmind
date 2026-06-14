import type { SlashCommand } from "../../types";

interface SlashMenuProps {
  commands: SlashCommand[];
  selectedIndex: number;
  onSelect: (cmd: SlashCommand) => void;
}

// Notion-style "/" command palette (format + AI actions) shown in the editor.
export default function SlashMenu({ commands, selectedIndex, onSelect }: SlashMenuProps) {
  return (
    <div className="absolute top-10 left-0 w-64 bg-slate-900 border border-slate-700 rounded-xl shadow-2xl z-[100] overflow-hidden">
      <div className="p-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
        Commands & AI
      </div>
      {commands.map((cmd, index) => (
        <div
          key={cmd.id}
          onClick={() => onSelect(cmd)}
          className={`flex items-center gap-3 px-4 py-2 cursor-pointer transition-colors ${
            index === selectedIndex
              ? "bg-indigo-600 text-white"
              : "hover:bg-slate-800 text-slate-300"
          }`}
        >
          <span
            className={`w-6 h-6 flex items-center justify-center rounded text-xs font-bold ${
              cmd.type === "ai" ? "bg-indigo-500/20 text-indigo-300" : "bg-slate-800"
            }`}
          >
            {cmd.icon}
          </span>
          <span className="text-sm font-medium">{cmd.label}</span>
        </div>
      ))}
    </div>
  );
}
