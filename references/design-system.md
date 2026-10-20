# Publication design system

These are conservative defaults, not substitutes for the current target journal instructions.

## Physical design

- Single-column width: 85–90 mm. Double-column width: 170–180 mm.
- Primary text: 8–9 pt at final size; never below 7 pt without an explicit journal requirement.
- Panel labels: 9–11 pt, semibold/bold, aligned to a shared anchor.
- Ordinary strokes: 0.6–1.2 pt. Emphasis should come mainly from hierarchy, not heavy outlines.
- Use no more than three visible text sizes and two font families in one figure.
- Preserve vector text and marks in SVG/PDF when possible. Raster microscopy separately at native resolution.

## Palette grammar

Assign color by semantic role, then freeze the mapping for the paper:

- `ink`: text, axes, outlines;
- `neutral`: context, reference, non-focus groups;
- `primary`: focal condition or method;
- `secondary`: the principal comparator;
- `support`: one or two supporting categories;
- `success` / `warning` / `failure`: only when those meanings are real;
- `sequential` or `diverging`: quantitative scales with a stated midpoint when diverging.

Prefer three to five semantic hues plus neutrals. Check colorblind distinguishability and grayscale ordering. Do not use red–green alone. Avoid decorative gradients, glow, glass, bevels, drop shadows, faux depth, and low-contrast pastel text.

## Layout grammar

- Make one panel visually dominant when the evidence has a primary result.
- Align plot areas, not just outer axes boxes.
- Reuse gutters, label anchors, baselines, legends, and color mappings.
- Put legends close to the data they decode and outside dense marks when possible.
- Use whitespace to group related evidence; do not box every element.
- Keep reading order unambiguous: left-to-right/top-to-bottom unless arrows establish another order.

## Corpus matching

The PubCNS corpus is a palette and composition precedent set. Match functional properties—contrast, saturation, number of accents, neutral balance, and visual weight—not the exact artwork. When no corpus match is appropriate, use a colorblind-first restrained palette.
