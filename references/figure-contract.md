# Figure contract

Write this contract before choosing colors or drawing. Keep it concise and save it in `figure-spec.json`.

## Required fields

- **core_claim**: one sentence the complete figure should support.
- **audience**: who must understand it and what they already know.
- **evidence**: supplied datasets, images, text, models, or assumptions.
- **evidence_status**: observed, derived, modelled, assumed, or illustrative for each component.
- **comparison**: the estimand or relationship being communicated.
- **uncertainty**: raw observations, interval definition, replicate structure, and missing-data treatment.
- **panel_roles**: context, primary evidence, validation, mechanism, boundary condition, or synthesis.
- **reading_order**: the intended visual path.
- **output_contract**: target journal, physical width, formats, backend, and editability requirements.
- **integrity_risks**: plausible ways the visual could overstate or distort the evidence.

## Stop conditions

Pause only the dependent rendering step when the supplied evidence cannot determine a requested value, grouping, label, uncertainty measure, or mechanism. Continue with a labelled wireframe or figure plan when that still helps.

Do not infer a causal arrow from correlation, a population claim from an uncontrolled sample, or a statistically significant result from visual separation alone.
