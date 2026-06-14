import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/layout/Layout";
import ChatPage from "./pages/ChatPage";
import MapPage from "./pages/MapPage";
import VaultPage from "./pages/VaultPage";
import EditorPage from "./pages/EditorPage";

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<ChatPage />} />
          <Route path="/map" element={<MapPage />} />
          <Route path="/vault" element={<VaultPage />} />
          <Route path="/editor" element={<EditorPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
