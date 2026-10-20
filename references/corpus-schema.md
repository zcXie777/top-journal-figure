# Corpus schema

The local PubCNS corpus stores metadata and derived visual features; it does not redistribute source artwork.

## `assets/generated/pubcns-cases.json`

Each case includes:

- `stable_id`, `content_hash`, `visual_hash`, `sequence`, `title`, canonical `journal`, `published_at`;
- `article_url`, `cover_url`, `thumbnail_url`, `msgid`, `itemidx`;
- `source_album`, `source_account`, schema version, and retrieval timestamp.

## `assets/generated/pubcns-style-index.json`

Each derived record includes:

- dominant colors with RGB/HEX/share and semantic role;
- image size/aspect ratio;
- whitespace, edge-density, saturation, luminance, and contrast proxies;
- visual tone, temperature, density, and weight hints;
- extraction version, status, and error field.

## `assets/curated/overrides.json`

Human-reviewed corrections live here and are merged at retrieval time. Keep them keyed by `stable_id`; never edit generated records directly.

The derived metrics are retrieval aids, not ground-truth claims about the originating journal. A PubCNS card labelled “Nature” is a curated secondary example, not an official Nature style specification.
