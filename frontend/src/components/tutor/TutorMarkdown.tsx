"use client";

import type { Components } from "react-markdown";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface TutorMarkdownProps {
  content: string;
  className?: string;
}

const mdComponents: Components = {
  h1: ({ children }) => (
    <h1 className="text-lg font-bold text-slate-900 mt-3 mb-2 first:mt-0">{children}</h1>
  ),
  h2: ({ children }) => (
    <h2 className="text-base font-bold text-slate-900 mt-3 mb-2 first:mt-0">{children}</h2>
  ),
  h3: ({ children }) => (
    <h3 className="text-sm font-semibold text-slate-800 mt-2 mb-1.5">{children}</h3>
  ),
  h4: ({ children }) => (
    <h4 className="text-sm font-semibold text-slate-800 mt-2 mb-1">{children}</h4>
  ),
  p: ({ children }) => <p className="text-sm leading-relaxed mb-2 last:mb-0">{children}</p>,
  ul: ({ children }) => (
    <ul className="list-disc pl-5 my-2 space-y-1 text-sm leading-relaxed">{children}</ul>
  ),
  ol: ({ children }) => (
    <ol className="list-decimal pl-5 my-2 space-y-1 text-sm leading-relaxed">{children}</ol>
  ),
  li: ({ children }) => <li className="marker:text-slate-500">{children}</li>,
  strong: ({ children }) => <strong className="font-semibold text-slate-900">{children}</strong>,
  em: ({ children }) => <em className="italic">{children}</em>,
  hr: () => <hr className="my-3 border-slate-200" />,
  blockquote: ({ children }) => (
    <blockquote className="border-l-4 border-blue-200 bg-blue-50/50 pl-3 py-1 my-2 rounded-r text-slate-700 text-sm">
      {children}
    </blockquote>
  ),
  a: ({ href, children }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-blue-600 hover:text-blue-800 underline underline-offset-2"
    >
      {children}
    </a>
  ),
  table: ({ children }) => (
    <div className="overflow-x-auto my-2 rounded-lg border border-slate-200">
      <table className="min-w-full text-xs border-collapse">{children}</table>
    </div>
  ),
  thead: ({ children }) => <thead className="bg-slate-100">{children}</thead>,
  th: ({ children }) => (
    <th className="border border-slate-200 px-2 py-1.5 text-left font-semibold text-slate-800">{children}</th>
  ),
  td: ({ children }) => (
    <td className="border border-slate-200 px-2 py-1.5 text-slate-700">{children}</td>
  ),
  code: ({ className, children, ...props }) => {
    const langMatch = /language-(\w+)/.exec(className || "");
    const text = String(children).replace(/\n$/, "");
    const multiline = text.includes("\n");
    if (langMatch || multiline) {
      return (
        <code
          className={`block w-full font-mono text-[13px] leading-relaxed text-slate-100 whitespace-pre-wrap ${className ?? ""}`}
          {...props}
        >
          {children}
        </code>
      );
    }
    return (
      <code
        className="bg-slate-200/90 text-slate-900 px-1.5 py-0.5 rounded text-[0.85em] font-mono"
        {...props}
      >
        {children}
      </code>
    );
  },
  pre: ({ children }) => (
    <pre className="bg-slate-900 text-slate-100 p-3 rounded-lg overflow-x-auto my-2 border border-slate-700 shadow-inner [&>code]:bg-transparent">
      {children}
    </pre>
  ),
};

/**
 * Renders AI tutor replies as formatted Markdown (headings, lists, code blocks, links, tables).
 */
export default function TutorMarkdown({ content, className = "" }: TutorMarkdownProps) {
  return (
    <div className={`tutor-md text-slate-700 ${className}`}>
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponents}>
        {content}
      </ReactMarkdown>
    </div>
  );
}
