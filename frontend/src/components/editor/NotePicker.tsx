import { useState } from "react";
import { FolderOpen } from "lucide-react";

interface NotePickerProps {
  notes: string[];
  onSelect: (filename: string) => void;
}

// "Open Note" dropdown listing the markdown files in raw_notes/.
export default function NotePicker({ notes, onSelect }: NotePickerProps) {
  const [open, setOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm text-slate-300 transition-colors border border-slate-700"
      >
        <FolderOpen size={16} /> Open Note
      </button>

      {open && (
        <div className="absolute top-full left-0 mt-2 w-64 bg-slate-800 border border-slate-700 rounded-lg shadow-xl z-50 max-h-64 overflow-y-auto">
          {notes.length === 0 ? (
            <div className="p-3 text-sm text-slate-500">No notes in raw_notes/</div>
          ) : (
            notes.map((note) => (
              <button
                key={note}
                onClick={() => {
                  onSelect(note);
                  setOpen(false);
                }}
                className="w-full text-left px-4 py-2 text-sm text-slate-300 hover:bg-indigo-600 hover:text-white transition-colors"
              >
                {note}
              </button>
            ))
          )}
        </div>
      )}
    </div>
  );
}
