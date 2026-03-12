"use client";

import { Choice } from "@/lib/types";

interface MultipleChoiceFormProps {
  choices: Choice[];
  selected: string | null;
  correctAnswer: string | null;
  onSelect: (label: string) => void;
  submitted: boolean;
}

export default function MultipleChoiceForm({
  choices,
  selected,
  correctAnswer,
  onSelect,
  submitted,
}: MultipleChoiceFormProps) {
  return (
    <div className="space-y-2">
      {choices.map((choice) => {
        let style = "border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50";
        if (submitted) {
          if (choice.label === correctAnswer) {
            style = "border-emerald-500 bg-emerald-50 text-emerald-800";
          } else if (choice.label === selected && choice.label !== correctAnswer) {
            style = "border-red-400 bg-red-50 text-red-800";
          } else {
            style = "border-slate-200 bg-slate-50 text-slate-400";
          }
        } else if (choice.label === selected) {
          style = "border-blue-500 bg-blue-50 text-blue-800";
        }

        return (
          <button
            key={choice.label}
            onClick={() => !submitted && onSelect(choice.label)}
            disabled={submitted}
            className={`w-full text-left px-4 py-3 rounded-lg border-2 transition-colors flex items-center gap-3 ${style} disabled:cursor-not-allowed`}
          >
            <span className="font-bold text-sm w-5 shrink-0">{choice.label}.</span>
            <span className="text-sm">{choice.text}</span>
            {submitted && choice.label === correctAnswer && (
              <span className="ml-auto text-emerald-600 text-lg">✓</span>
            )}
            {submitted && choice.label === selected && choice.label !== correctAnswer && (
              <span className="ml-auto text-red-500 text-lg">✗</span>
            )}
          </button>
        );
      })}
    </div>
  );
}
