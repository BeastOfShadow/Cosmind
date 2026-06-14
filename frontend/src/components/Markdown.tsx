import ReactMarkdown, { type Components } from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import { resolveAsset } from "../lib/config";

interface MarkdownProps {
  content: string;
  /** Tailwind classes applied to rendered <img> tags (varies per surface). */
  imgClassName?: string;
}

// Shared markdown renderer: LaTeX (KaTeX) support + asset-path rewriting for
// images and links. Used by the chat, the editor preview and the AI panel.
export default function Markdown({ content, imgClassName = "" }: MarkdownProps) {
  const components: Components = {
    img: ({ src, alt, ...props }) => (
      <img src={resolveAsset(typeof src === "string" ? src : undefined)} alt={alt || ""} {...props} className={imgClassName} />
    ),
    a: ({ href, children, ...props }) => (
      <a
        href={resolveAsset(href)}
        target="_blank"
        rel="noopener noreferrer"
        className="text-indigo-400 hover:text-indigo-300 transition-colors underline"
        {...props}
      >
        {children}
      </a>
    ),
  };

  return (
    <ReactMarkdown
      remarkPlugins={[remarkMath]}
      rehypePlugins={[rehypeKatex]}
      components={components}
    >
      {content}
    </ReactMarkdown>
  );
}
