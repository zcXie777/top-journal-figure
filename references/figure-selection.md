# Figure-type selection gate

Use this gate after inspecting the evidence and before writing rendering code or generating an image. Its purpose is to give the user control over the exact visual form without asking them to understand every available chart type.

## Selection rules

1. Infer the evidence goal, data structure, sample pairing, dimensionality, uncertainty, and intended reading order.
2. Offer three to five compatible choices. These may be individual plots or complete multi-panel compositions.
3. Put the strongest recommendation first and label it `Recommended`.
4. For every option, state the main advantage and one real limitation in a single sentence.
5. Include automatic selection as an option, but do not treat silence as consent.
6. Wait for the user's answer. Do not render previews, diagrams, or final figures while the choice is unresolved.
7. If the user explicitly asks to bypass selection, state the automatically chosen type before rendering and record the bypass in the figure specification.

An exact user-specified type counts as confirmation. If it would distort the evidence—for example, a bar chart hiding paired observations—explain the problem and offer compatible alternatives before proceeding.

## Candidate routing

Choose candidates by inferential job, not novelty:

| Evidence structure | Strong candidates |
|---|---|
| Independent group comparison | box plus points; violin plus points; raincloud; dot-range |
| Paired or repeated measures | paired dot plot; spaghetti plot; within-subject slopegraph; paired raincloud |
| Continuous trend | line plus interval; raw trajectories; small multiples; model curve plus interval |
| Distribution | ECDF; histogram; density; ridgeline; raincloud |
| Relationship | scatter plus fit; hexbin; contour; faceted scatter |
| Composition | normalized stacked bars; heatmap; mosaic; alluvial/Sankey when transitions are real |
| High-dimensional structure | PCA; UMAP/t-SNE; clustered heatmap; dot plot |
| Process | staged flow; swimlane; experimental timeline; cohort/CONSORT flow |
| Architecture | layered architecture; data-flow diagram; module interaction map |
| Mechanism | entity–interaction schematic; pathway map; hypothesis model with evidence-status encoding |
| Spatial evidence | representative image plus ROI; segmentation overlay; map plus quantification |
| Manuscript story | method-to-evidence; claim escalation; hero plus satellites; paired comparison; matrix |

Avoid offering forms that are invalid for the supplied data. Do not recommend pie charts for many categories, 3-D charts, bars that hide replicate structure, dual axes without a compelling shared interpretation, or causal diagrams unsupported by the evidence.

## Prompt shape

Keep the user-facing choice compact. Example:

> Based on these independent groups, choose the figure form:
> 1. Box plot + raw points — Recommended; compact and preserves observations, but distribution shape is only partly visible.
> 2. Raincloud — shows distribution and observations, but needs more horizontal space.
> 3. Violin + points — emphasizes distribution shape, but can overstate smoothness at small n.
> 4. Let the skill choose automatically.

For a multi-panel request, offer complete compositions rather than forcing the user to choose every panel separately. After selection, summarize the frozen composition in one sentence and proceed.

## Specification record

Store a `selection` object in `figure-spec.json`:

```json
{
  "selection": {
    "mode": "user_confirmed",
    "chosen_type": "box-plus-points",
    "candidates": ["box-plus-points", "raincloud", "violin-plus-points"],
    "reason": "Independent groups with visible biological replicates"
  }
}
```

Allowed modes are `user_confirmed`, `user_specified`, and `explicit_auto_bypass`.
