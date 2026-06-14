import type { ReactNode } from "react";

// --- Chat ---
export interface Source {
  source: string;
  content: string;
}

export interface ChatMessage {
  role: "user" | "bot";
  content: string;
  sources?: Source[];
}

// --- Vault ---
export interface VaultDoc {
  id?: string;
  source: string;
  chunk_index: number;
  chunk_total: number;
  preview: string;
  content: string;
}

export interface VaultData {
  documents: VaultDoc[];
  total: number;
  sources?: number;
  error?: string;
}

export interface NoteChunk {
  chunk_index: number;
  chunk_total: number;
  content: string;
}

export interface SimilarNote {
  source: string;
  score: number;
}

export interface NoteDetail {
  source: string;
  content: string;
  on_disk: boolean;
  chunks: NoteChunk[];
  similar: SimilarNote[];
  error?: string;
  detail?: string; // FastAPI 404 message
}

// --- Map / Visualizer ---
export interface MapTrace {
  x: number[];
  y: number[];
  z?: number[];
  texts: string[];
  hovertexts?: string[];
  name: string;
}

export interface GraphNode {
  id: string;
  name: string;
  val: number;
  preview: string;
}

export interface GraphLink {
  source: string;
  target: string;
  similarity: number;
}

export interface MapData {
  traces3D: MapTrace[];
  traces2D: MapTrace[];
  graph: { nodes: GraphNode[]; links: GraphLink[] };
  error?: string;
}

// --- Editor ---
export type SaveStatus = "idle" | "saving" | "saved" | "error";
export type ViewMode = "edit" | "preview" | "split";

export interface SlashCommand {
  id: string;
  label: string;
  icon: ReactNode;
  syntax: string;
  type?: "ai" | "format";
}

export interface Attachment {
  fullMatch: string;
  isImage: boolean;
  label: string;
  path: string;
  filename: string;
}
