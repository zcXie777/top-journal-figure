# Contributing

Contributions that improve evidence faithfulness, figure selection, accessibility,
editability, corpus maintenance, or reproducible validation are welcome.

## Before opening a pull request

1. Keep `SKILL.md` concise and route detailed procedures to focused references.
2. Do not add source article images, paywalled material, benchmark images, or assets whose
   redistribution rights are unclear.
3. Record any newly reviewed public project or dataset in
   `references/source-audit.md`, including its live URL, license/status, and review date.
4. Put generated corpus updates only in `assets/generated/`; put human corrections only
   in `assets/curated/overrides.json`.
5. Preserve stable IDs and increment `schema_version` only for breaking field changes.
6. Add or update an evidence-based test when behavior changes.

Run the offline checks:

```powershell
python tests/smoke_test.py
python scripts/validate_release.py
python scripts/validate_figure_spec.py assets/example-figure-spec.json
```

For corpus changes, run `python scripts/update_corpus.py --check` first and include the
added/changed/removed summary in the pull request. Do not make network-dependent refreshes
part of ordinary CI.

By submitting a contribution, you agree that it is licensed under Apache-2.0 and that you
have the right to submit it.

