// Backend endpoints (single source of truth for the whole frontend)
export const API_URL = "http://localhost:8000/api";
export const ASSETS_URL = "http://localhost:8000/assets";

// Rewrites a relative "assets/..." path to the backend static URL.
// Leaves absolute / external URLs untouched.
export const resolveAsset = (src?: string): string | undefined =>
  src?.startsWith("assets/") ? `${ASSETS_URL}/${src.split("assets/")[1]}` : src;
