import { useState, useEffect } from "react";
import { Database } from "lucide-react";
import { API_URL } from "../lib/config";
import type { VaultData } from "../types";

// Browse the vectorized chunks currently stored in ChromaDB.
export default function VaultPage() {
  const [vaultData, setVaultData] = useState<VaultData>({ documents: [], total: 0 });
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
        <h2 className="text-2xl font-semibold opacity-80">Explore Database</h2>
        <p className="text-slate-400 mt-1">
          {loading
            ? "Reading DB..."
            : `Total vectorized chunks (fragments): ${vaultData.total}`}
        </p>
      </header>

      {vaultData.total === 0 && !loading ? (
        <div className="flex-1 flex flex-col items-center justify-center border-2 border-dashed border-slate-700 rounded-xl opacity-50">
          <Database size={48} className="mb-4" />
          <p>The database is empty. Process some notes to get started.</p>
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
              <div className="text-sm text-slate-300 italic">"{doc.preview}"</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
