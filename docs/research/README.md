# Research document (LaTeX)

- **Source:** [`research-plan.tex`](research-plan.tex) — research plan and working report for the adaptive CS learning system.
- **Compile (local):** requires a LaTeX distribution with `amsmath`, `graphicx`, `url`, `tikz` (`arrows.meta`, `positioning`), `float`, `placeins`.

```bash
cd docs/research
pdflatex -interaction=nonstopmode research-plan.tex
pdflatex -interaction=nonstopmode research-plan.tex   # second pass for TOC/refs
```

Build artifacts (`*.aux`, `*.log`, `*.pdf`, etc.) are ignored by the repo root `.gitignore` under `docs/`.

For the **implemented** system (APIs, schema, flows), see [../SYSTEM_DESIGN.md](../SYSTEM_DESIGN.md).
