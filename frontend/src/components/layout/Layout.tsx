import type { ReactNode } from "react";
import Sidebar from "./Sidebar";

// App shell: persistent sidebar + routed page content.
export default function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="flex h-screen bg-slate-900 text-slate-100 font-sans overflow-hidden">
      <Sidebar />
      <main className="flex-1 flex overflow-hidden">{children}</main>
    </div>
  );
}
