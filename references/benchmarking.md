# Evaluation protocol

Evaluate behavior, not prompt wording.

## Core test set

Maintain representative tasks for:

1. small-n group comparison with raw points and uncertainty;
2. time-course with repeated measures;
3. dense heatmap with missing values;
4. multi-panel claim escalation;
5. method workflow with editable connectors;
6. mechanism hypothesis with explicit evidence boundaries;
7. image-plus-quantification layout;
8. colorblind and grayscale stress tests.

## Rubric

Score each dimension from 0–4:

- evidence faithfulness;
- inferential clarity;
- final-size legibility;
- semantic palette consistency;
- accessibility;
- editability and reproducibility;
- journal/export compliance;
- visual economy.

Any invented datum, statistic, or mechanism is an automatic failure regardless of appearance.

## Optional public benchmarks

- Use ChartMimic for breadth across chart-to-code types.
- Use FigMirror for deterministic rendering and code/figure reproducibility.
- Use SciFigAlign to test manuscript–figure alignment, after checking sample provenance.
- Use license-cleared SciFormaData rows for diagram-structure evaluation.

Do not ship benchmark images inside this skill. Store only task identifiers, scores, and source links unless redistribution is explicitly permitted.
