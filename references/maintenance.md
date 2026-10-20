# Maintenance and updates

The update path is deliberately separate from figure generation.

## Versioned layers

1. `assets/sources.json` — hand-maintained source registry and license/status notes.
2. `assets/generated/` — reproducible outputs; never hand-edit.
3. `assets/curated/overrides.json` — stable-ID corrections and editorial tags.
4. `assets/catalog-manifest.json` — schema, extractor, source, and corpus versions.

## Safe refresh

Run `python scripts/update_corpus.py --check` first. It downloads into a temporary directory, reports added/changed/removed stable IDs, and makes no changes. Run without `--check` to atomically replace generated files only after ingestion, feature extraction, and validation succeed.

Each record uses `wechat:<msgid>:<itemidx>` as its stable ID. `content_hash` detects metadata changes; `visual_hash` tracks image inputs. The style extractor refreshes metadata but reuses visual features whenever `visual_hash` and the extractor version are unchanged.

Never overwrite curated overrides during refresh. A missing source item is reported as removed but remains recoverable from version control or the previous atomic output.

## External-source updates

Record the reviewed URL, license, review date, and optionally commit/tag in `references/source-audit.md`. External projects and Hugging Face datasets are optional evaluation inputs, not runtime dependencies. Promote an upstream implementation into this skill only after code review, license review, attribution, and isolated tests.

## Schema evolution

Increase `schema_version` only for breaking field changes. Add compatible fields without renaming old ones. When a breaking change is unavoidable, add a migration script before changing the reader.
