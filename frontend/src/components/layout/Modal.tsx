import { useEffect, type ReactNode } from "react";
import { X } from "lucide-react";

interface ModalProps {
  open: boolean;
  onClose?: () => void; // omit to make modal non-dismissable (e.g. while busy)
  title?: string;
  children: ReactNode;
}

// Centered overlay dialog. Click backdrop or Esc to close (when onClose given).
export default function Modal({ open, onClose, title, children }: ModalProps) {
  useEffect(() => {
    if (!open || !onClose) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={() => onClose?.()}
    >
      <div
        className="relative w-full max-w-md mx-4 rounded-xl bg-slate-900 border border-slate-700 shadow-2xl p-6"
        onClick={(e) => e.stopPropagation()}
      >
        {onClose && (
          <button
            onClick={onClose}
            className="absolute top-3 right-3 text-slate-400 hover:text-slate-200"
            title="Close"
          >
            <X size={18} />
          </button>
        )}
        {title && <h2 className="text-lg font-semibold text-slate-100 mb-4 pr-6">{title}</h2>}
        {children}
      </div>
    </div>
  );
}
