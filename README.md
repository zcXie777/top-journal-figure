# Top Journal Figure

An evidence-first Codex skill for publication-grade scientific figures, workflows,
mechanism diagrams, multi-panel results, and graphical abstracts.

`Top Journal Figure` turns a scientific claim, dataset, manuscript paragraph, or rough
sketch into an editable and reproducible figure package. It uses a locally maintained
corpus of 122 PubCNS/WeChat color-study records as visual precedents while preserving
the meaning, uncertainty, and provenance of the supplied evidence.

## Why this skill is different

- **Choose before rendering.** The skill recommends 3–5 compatible figure types and
  waits for the user to select one. It proceeds automatically only when the user
  explicitly asks to skip selection.
- **Evidence before decoration.** Values, units, replicates, uncertainty, missingness,
  and evidence status are preserved in a figure contract.
- **Top-journal visual precedent.** Palette and composition properties are retrieved
  from the local 122-case style index; source artwork is never traced or redistributed.
- **Editable delivery.** Data figures include source code, SVG/PDF, PNG preview,
  `figure-spec.json`, `palette.json`, and `qa.json`.
- **Updateable by design.** Corpus ingestion, style extraction, curated overrides,
  manifests, and safe atomic updates are separated.

## Quick start

Place this repository at:

```text
<CODEX_HOME>/skills/top-journal-figure
```

When `CODEX_HOME` is not configured, the usual Windows location is:

```text
%USERPROFILE%/.codex/skills/top-journal-figure
```

Then invoke it in Codex:

```text
使用 $top-journal-figure，根据我的数据制作论文插图。
```

The skill first responds with a compact selection such as:

```text
1. Box plot + raw points — Recommended; preserves the observations.
2. Raincloud plot — reveals distribution shape but needs more width.
3. Violin + points — compact, but smoothing can mislead at small n.
4. Let the skill choose automatically.
```

It renders only after the figure type is confirmed, unless the request explicitly says
to skip selection and proceed automatically.

## Supported work

The routing system covers group comparisons, distributions, trends, relationships,
composition, high-dimensional data, statistics/model diagnostics, networks, spatial
evidence, workflows, architectures, mechanisms, and graphical abstracts. Common forms
include box/violin/raincloud plots, survival curves, scatter and regression plots,
heatmaps, volcano plots, PCA/UMAP, forest plots, Sankey diagrams, experimental workflows,
pathway schematics, and multi-panel manuscript figures.

## Repository layout

```text
top-journal-figure/
├─ SKILL.md                    # Skill entry point and workflow
├─ agents/openai.yaml          # Codex display metadata
├─ assets/                     # Corpus, archetypes, and curated overrides
├─ references/                 # Selection, design, provenance, and maintenance rules
├─ scripts/                    # Corpus update, recommendation, and validation tools
├─ tests/                      # Offline smoke tests
└─ examples/                   # Reproducible demonstration figure
```

## Corpus updates

Install the updater dependencies:

```powershell
python -m pip install -r requirements.txt
```

Preview a refresh without changing the tracked corpus:

```powershell
python scripts/update_corpus.py --check
```

Apply an update only after reviewing the added, changed, and removed stable IDs:

```powershell
python scripts/update_corpus.py
```

Generated corpus files must never be edited by hand. Corrections belong in
`assets/curated/overrides.json`. See
[`references/maintenance.md`](references/maintenance.md) for the versioning contract.

## Development and validation

```powershell
python -m pip install -r requirements-dev.txt
python tests/smoke_test.py
python scripts/validate_release.py
python scripts/validate_figure_spec.py assets/example-figure-spec.json
```

The included GitHub Actions workflow runs the offline checks on pull requests and pushes.
Network-dependent corpus refreshes are deliberately excluded from CI.

## Example

The repository includes a deterministic synthetic single-cell example combining a
workflow, embedding, marker heatmap, and donor-level composition. Every value is labelled
as synthetic and the editable source accompanies the render.

![Synthetic single-cell demonstration](examples/synthetic-scrna-workflow/top_journal_demo.png)

## Data and licensing

Original code and documentation in this repository are licensed under Apache-2.0.
Third-party article titles, URLs, journal names, trademarks, and source visual works remain
the property of their respective owners. No source artwork is bundled. Read
[`DATA_AND_THIRD_PARTY_NOTICE.md`](DATA_AND_THIRD_PARTY_NOTICE.md) before redistributing a
corpus build.

## 中文简介

这是一个面向科研论文插图的 Codex skill。它会先检查数据和证据结构，再给出 3–5
个适合的图型供用户选择；确认后才开始绘制。输出包含可编辑矢量图、PNG 预览、
Python/R 源码、图形规格、配色映射和质量检查记录。语料库使用122篇“跟着顶刊学配色”
文章的元数据与派生视觉特征，但不包含或重新分发原始文章图片。

