---
name: top-journal-figure
description: Create, redesign, and audit publication-grade scientific plots, multi-panel figures, workflows, mechanisms, and graphical abstracts using evidence-first figure contracts, corpus-derived top-journal visual patterns, editable outputs, and rendered quality checks. Use for manuscript figures and scientific illustrations; not for decorative art or unsupported data generation.
---

# Top Journal Figure

Turn a scientific claim and its evidence into a clear, editable, reproducible figure. Style follows the evidence architecture; never use aesthetics to hide uncertainty or compensate for an unsupported claim.

## Start with a figure-type selection gate

Before rendering, inspect the supplied evidence and read [references/figure-selection.md](references/figure-selection.md). If the user has not already named an exact figure type or panel composition, present three to five suitable choices. Put the recommended option first and give one short reason and one meaningful tradeoff for each. Wait for the user's selection before drawing.

An explicit request such as “skip selection,” “directly render,” or “choose automatically and proceed” bypasses the wait. A vague request such as “make a figure,” “try it,” or “use any data” does not bypass it. When the user names an exact type, treat that type as selected unless it conflicts with the evidence; explain the conflict and offer alternatives instead of silently substituting another form.

After the type is selected, infer answered settings and ask only for the remaining choices, preferably in the same compact prompt when that does not obscure the type decision:

1. **Evidence goal** — compare, trend, distribution, relationship, composition, process, mechanism, spatial, or auto.
2. **Figure type** — the exact plot, schematic, or multi-panel composition confirmed at the selection gate.
3. **Visual tone** — restrained, contrast-led, vivid-but-controlled, colorblind-first, or corpus match.
4. **Delivery** — draft, manuscript single-column, manuscript double-column, presentation; plus target journal and Python/R when applicable.

Defaults after type confirmation are `auto` evidence goal, `corpus match`, and `manuscript double-column`. Reuse an established Python/R preference. Do not ask about a plotting backend for a non-data schematic.

## Required workflow

1. Read [references/figure-contract.md](references/figure-contract.md) and write a concise figure contract before drawing.
2. Read [references/taxonomy.md](references/taxonomy.md), recommend compatible exact figure types, and complete the selection gate. Do not render while selection is unresolved.
3. Read [references/design-system.md](references/design-system.md) before choosing layout, palette, typography, or export dimensions.
4. When the local corpus index exists, run `scripts/recommend_style.py` to retrieve relevant PubCNS/top-journal palette precedents. Treat retrieved cases as inspiration, never as templates to trace.
5. For a selected multi-panel or schematic form, produce two or three low-cost internal layout plans when layout is consequential. Rank them by faithfulness, inferential clarity, readability at final size, accessibility, editability, and visual economy; render only the best unless the user asks to compare candidates.
6. Record the confirmed type, candidate types, and selection mode in `figure-spec.json`.
7. Use deterministic code for data-bearing marks. Generative imagery may support clearly explanatory, non-data-bearing schematics, but must not be presented as observed evidence.
8. Deliver editable source, vector master where possible, raster preview, figure specification, palette mapping, and a short QA record.

## Evidence rules

- Preserve values, units, categories, exclusions, missingness, sample structure, uncertainty, and statistical meaning.
- Never invent measurements, sample sizes, error bars, significance, thresholds, labels, or biological mechanisms.
- Distinguish observed, derived, modelled, assumed, and illustrative content in the specification and legend.
- Show raw observations when practical; state what error bars and intervals mean.
- Use area, volume, or perspective only when the encoded quantity justifies it. Avoid 3-D charts.
- Keep one stable semantic color mapping across all figures in the same paper.

## Artifact contract

For a data-bearing figure, return:

- plotting source (`.py` or `.R`), with deterministic seeds where randomness is used;
- `figure-spec.json` following [references/figure-spec.schema.json](references/figure-spec.schema.json);
- editable/vector output (`.svg` and/or `.pdf`) and a PNG preview;
- `palette.json` mapping semantic roles to colors;
- `qa.json` recording final dimensions, minimum text size, color checks, clipping/overlap review, and any exemptions.

For workflows and schematics, prefer editable SVG or Draw.io plus PDF/PNG exports. Record icon and external-asset provenance.

## Quality gate

Inspect the final render at its intended physical size. Block delivery when labels are clipped, comparable panels are misaligned, legends obscure data, contrast is insufficient, palette semantics drift, statistical encodings are ambiguous, or only a non-editable raster survives. A visually attractive figure that weakens or misstates the evidence fails.

## Corpus, maintenance, and evaluation

- To refresh the 122-item WeChat corpus, read [references/maintenance.md](references/maintenance.md) and [references/corpus-schema.md](references/corpus-schema.md), then run `scripts/update_corpus.py`.
- Keep generated corpus data separate from curated overrides. Never hand-edit generated files.
- To evaluate against public corpora, read [references/benchmarking.md](references/benchmarking.md).
- To review upstream inspirations and license boundaries, read [references/source-audit.md](references/source-audit.md). Do not copy an upstream asset or implementation unless its license and attribution requirements are recorded.
