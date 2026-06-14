import { FileText, Trash2 } from "lucide-react";
import { ASSETS_URL } from "../../lib/config";
import type { Attachment } from "../../types";

interface AttachmentBarProps {
  attachments: Attachment[];
  onDelete: (fullMatch: string, filename: string) => void;
}

// Floating strip of uploaded assets (images/PDFs) parsed from the note body.
export default function AttachmentBar({ attachments, onDelete }: AttachmentBarProps) {
  return (
    <div className="absolute bottom-4 left-4 right-4 bg-slate-900/80 backdrop-blur-md border border-slate-700 rounded-xl p-3 flex gap-4 overflow-x-auto shadow-2xl z-40">
      <div className="flex items-center text-xs font-semibold text-slate-500 uppercase tracking-wider pl-2 pr-4 border-r border-slate-700/50">
        Attachments
      </div>
      {attachments.map((att, idx) => (
        <div
          key={idx}
          className="flex items-stretch bg-slate-800 rounded-lg overflow-hidden border border-slate-700 group hover:border-indigo-500/50 transition-colors flex-shrink-0"
        >
          <a
            href={`${ASSETS_URL}/${att.filename}`}
            target="_blank"
            rel="noopener noreferrer"
            className="p-2 bg-slate-900 flex items-center justify-center min-w-[3rem] hover:bg-slate-700 transition-colors"
          >
            {att.isImage ? (
              <img
                src={`${ASSETS_URL}/${att.filename}`}
                alt={att.label}
                className="w-8 h-8 object-cover rounded shadow ring-1 ring-slate-800"
              />
            ) : (
              <FileText size={20} className="text-slate-400" />
            )}
          </a>

          <div className="flex flex-col justify-center px-3 py-1 flex-1">
            <div
              className="text-xs font-medium text-slate-300 max-w-[120px] truncate"
              title={att.filename}
            >
              {att.filename}
            </div>
            <div className="text-[10px] text-slate-500 uppercase">
              {att.isImage ? "Image" : "Document"}
            </div>
          </div>

          <button
            onClick={() => onDelete(att.fullMatch, att.filename)}
            title="Delete"
            className="px-3 flex items-center justify-center bg-red-950/30 text-red-400 hover:bg-red-600 hover:text-white transition-colors border-l border-slate-700"
          >
            <Trash2 size={14} />
          </button>
        </div>
      ))}
    </div>
  );
}
