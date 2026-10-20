# Scientific figure taxonomy

Select by inferential role first, then by visual form.

| Evidence goal | Preferred forms | Common misuse |
|---|---|---|
| Compare magnitude | dot/range, box/violin plus points, restrained bars | hiding replicates; truncated axes without disclosure |
| Show trend | line plus interval, small multiples | connecting unrelated categories; smoothing without method |
| Show distribution | ECDF, histogram, density, raincloud | over-smoothed density; unequal bins |
| Show relationship | scatter, hexbin, contour, regression with interval | causal wording; overplotting; omitted groups |
| Show composition | normalized bars, mosaic, heatmap | pie charts with many slices; absolute/relative confusion |
| Show hierarchy | tree, dendrogram, nested layout | area implying magnitude when none exists |
| Show process | staged flow, swimlane, state diagram | decorative arrows; ambiguous direction |
| Show mechanism | entity–interaction schematic plus evidence panels | presenting a hypothesis as established fact |
| Show spatial evidence | registered image, map, segmentation overlay | altered imagery; missing scale/projection |
| Show high-dimensional structure | heatmap, PCA/UMAP, network | treating embedding distance as calibrated measurement |

## Multi-panel archetypes

- **Claim escalation**: context → primary effect → mechanism → validation.
- **Hero plus satellites**: one dominant evidence panel with compact supporting panels.
- **Method to evidence**: workflow/architecture followed by quantitative validation.
- **Paired comparison**: matched conditions with identical geometry and scales.
- **Spatial plus quantification**: representative image, segmentation/ROI, summary statistics.
- **Matrix**: rows encode conditions and columns encode evidence types; use only when repeated comparison is the message.

Every labelled panel must have a distinct inferential role. Multiple panels showing the same claim with different decorative forms add noise, not evidence.
