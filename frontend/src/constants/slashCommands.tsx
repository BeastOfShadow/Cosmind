import { Search, CheckCircle, GraduationCap } from "lucide-react";
import type { SlashCommand } from "../types";

// Slash-menu commands for the note editor. Format commands insert markdown
// syntax; "ai" commands call the editor copilot endpoint.
export const SLASH_COMMANDS: SlashCommand[] = [
  { id: "h1", label: "Heading 1", icon: "H1", syntax: "# " },
  { id: "h2", label: "Heading 2", icon: "H2", syntax: "## " },
  { id: "h3", label: "Heading 3", icon: "H3", syntax: "### " },
  { id: "image", label: "Image", icon: "🖼️", syntax: "![Description](assets/image_name.png)\n" },
  { id: "pdf", label: "PDF Embed", icon: "📄", syntax: "[Download PDF](assets/document.pdf)\n" },
  { id: "todo", label: "To-do List", icon: "☑", syntax: "- [ ] " },
  { id: "list", label: "Bulleted List", icon: "•", syntax: "- " },
  { id: "quote", label: "Quote", icon: "“", syntax: "> " },
  { id: "code", label: "Code Block", icon: "<>", syntax: "```\n\n```" },
  { id: "divider", label: "Divider", icon: "—", syntax: "---\n" },
  { id: "ai-expand", label: "Expand Knowledge", icon: <Search size={14} />, syntax: "expand", type: "ai" },
  { id: "ai-validate", label: "Validate Sources", icon: <CheckCircle size={14} />, syntax: "validate", type: "ai" },
  { id: "ai-tutor", label: "Help & Tutor", icon: <GraduationCap size={14} />, syntax: "tutor", type: "ai" },
];
