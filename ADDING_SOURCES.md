# Adding K-12 AI Resource Sources

The resource scanner supports two kinds of sources:

1. **Catalog sources** (mode: "catalog")
   - Curated lists of datasets, benchmarks, or models with structured metadata
   - Custom parser required (e.g., `"parser": "kaiip"` for the K-12 AI Infrastructure platform)
   - Example: K-12 AI Infrastructure Program datasets page with HTML cards

2. **Monitor sources** (mode: "monitor")
   - Resource hubs or news pages with best-effort link extraction
   - Generic keyword-based link detection
   - Useful for discovering new datasets/benchmarks without a dedicated parser
   - Example: Hugging Face, DrivenData, Learning Commons

## Add a Source

Edit:

```text
data/source-watchlist.json
```

### For a catalog (if you write a parser):

```json
{
  "name": "Example Catalog",
  "type": "Curated catalog",
  "mode": "catalog",
  "parser": "example",
  "url": "https://example.org/datasets/",
  "keywords": ["dataset", "benchmark", "model", "education", "k-12"]
}
```

Then add the parser function to `scripts/scan-resources.mjs`.

### For a monitor (simple keyword extraction):

```json
{
  "name": "Example Hub",
  "type": "Resource hub",
  "mode": "monitor",
  "url": "https://example.org/datasets/",
  "linkPattern": "/datasets/[^\"'/]+",
  "keywords": ["dataset", "benchmark", "model", "education", "k-12", "math", "science"]
}
```

Use `linkPattern` (a regex) to filter links. `keywords` are used to match relevant links on the page.

## Good Keywords for K-12 Resources

- `dataset`, `benchmark`, `model`, `corpus`, `competition`
- `k-12`, `grade school`, `elementary`, `middle school`, `high school`
- `student`, `teacher`, `classroom`, `tutoring`
- `math`, `science`, `reading`, `literacy`, `writing`
- `assessment`, `grading`, `evaluation`
- `nlp`, `ai`, `machine learning`, `annotation`

## Current Watchlist

The starter watchlist includes:

- **K-12 AI Infrastructure Program** (catalog) — 9 curated datasets (GSM8k, Bridge, SciQ, etc.)
- **DrivenData Competitions** (monitor) — Education-relevant data science challenges
- **Learning Commons** (monitor) — Open infrastructure for K-12 AI
- **Hugging Face Education Datasets** (monitor) — Community datasets and models
- **Linguistic Data Consortium** (monitor) — Language and annotation corpora
