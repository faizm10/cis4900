"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useLearnerStore } from "@/store/learnerStore";

export default function NavBar() {
  const pathname = usePathname();
  const { learnerId, goalKcName } = useLearnerStore();

  const links = [
    { href: "/", label: "Home" },
    { href: "/map", label: "Map" },
    { href: "/activity", label: "Practice" },
    { href: "/progress", label: "Progress" },
    { href: "/admin", label: "Admin" },
  ];

  return (
    <nav className="bg-white border-b border-slate-200 shadow-sm">
      <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <span className="font-bold text-blue-600 text-lg">CS Learning Map</span>
          <div className="flex items-center gap-1">
            {links.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={`px-3 py-1.5 rounded text-sm font-medium transition-colors ${
                  pathname === link.href
                    ? "bg-blue-100 text-blue-700"
                    : "text-slate-600 hover:bg-slate-100"
                }`}
              >
                {link.label}
              </Link>
            ))}
          </div>
        </div>
        <div className="flex items-center gap-2 text-sm text-slate-500">
          {learnerId && (
            <>
              <span className="bg-slate-100 px-2 py-1 rounded text-slate-700 font-medium">
                {learnerId}
              </span>
              {goalKcName && (
                <span className="text-slate-400">→ <span className="text-blue-600">{goalKcName}</span></span>
              )}
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
