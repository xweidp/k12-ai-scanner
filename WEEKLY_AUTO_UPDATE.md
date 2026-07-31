# Weekly Auto-Update System for K-12 AI Inventory

Your K-12 dataset inventory now **automatically updates every Monday at 8 AM Central** with newly discovered K-12 AI education resources.

## How It Works

Every Monday, GitHub Actions runs:

### 1. Generic Monitor-Source Scan (`scan-resources.py`)
- Scans 7+ education resource sites (DrivenData, OpenAI, Learning Commons, IEEE Dataport, Papers With Code, etc.)
- Finds education-related competitions, benchmarks, and resources
- Non-programmatic (doesn't require API keys)

### 2. GitHub & Hugging Face Direct Search (`scan-github-hf.py`)
- **GitHub**: Searches for K-12 education repos with data/artifacts (7 targeted queries)
- **Hugging Face**: Searches HF datasets hub for K-12 education (7 targeted queries)
- Programmatic search using public APIs
- Deduplicates against existing inventory

### 3. Inventory Merge & Update (`update-inventory.py`)
- Combines all discovered resources
- Deduplicates against your existing v18 base inventory (96 records)
- Adds **discovery_date** timestamp to each new resource
- Saves updated inventory with **new records flagged for review**
- Maintains all existing v18 classifications & tier data

### 4. Git Commit
- Commits updated inventory to GitHub
- Auto-deploys to GitHub Pages if configured

---

## What Gets Updated

Each Monday scan produces:

| File | Contents |
|------|----------|
| `data/resources.json` | Generic monitor-source scan results (64 resources in test) |
| `data/github_hf_scan_results.json` | GitHub/HF direct search results (62 resources in test) |
| `data/all_scanned_resources.json` | Merged deduplicated results (112 new in test) |
| `data/k12_inventory_latest.csv` | Full updated inventory (96 base + ~112 new = 208 total) |
| `data/discovery_summary.json` | Summary stats (by source, type, subject) |

---

## New Resources Workflow

### Initial Test Run Results (July 31, 2026)

```
Base Inventory (v18):           96 records ✓ VERIFIED (20/20 links working)
Monitor-source scan:           +50 new records
GitHub/HF direct search:       +62 new records
Total discoverable:           208 records (96 existing + 112 new)
```

**Breakdown of new discoveries:**

Monitor Sources:
- OpenAI Research: 20
- DrivenData: 10
- IEEE Dataport: 8
- Learning Commons: 6
- Papers With Code: 4
- Others: 2

GitHub/HF Direct:
- Hugging Face datasets: 52
- GitHub repositories: 10

Resource Types:
- Datasets: 64
- Benchmarks: 15
- Competitions: 8
- Models: 3

---

## Review & Filter Recommendations

New resources come in flagged as **"Not Reviewed: newly discovered"** with:
- `discovery_date`: When found (YYYY-MM-DD)
- `discovery_source`: Where found (GitHub, HF, DrivenData, etc.)
- `fit_score`: Relevance score (0-100, based on keyword matching)
- `subject_area`: Detected K-12 subjects (Math, Science, etc.)

### Before sharing with coworkers:

1. **Filter by fit_score**: Only show resources with score >= 70
2. **Filter by source**: HF/GitHub require more scrutiny (not pre-audited)
3. **Quick spot-check**: Sample 10-20 new resources to verify K-12 relevance
4. **Update discovery_date field**: Make it human-readable if needed

---

## Manual Triggers

Run a scan immediately without waiting for Monday:

```bash
# Trigger workflow from GitHub
# Go to: https://github.com/xweidp/k12-ai-scanner/actions
# Click "Weekly K-12 Resource Scan & Inventory Update"
# Click "Run workflow" → "Run workflow"
```

Or run locally:

```bash
# Generic monitor sources
python3 scan-resources.py

# GitHub/HF direct search
python3 scan-github-hf.py

# Merge results
python3 update-inventory.py
```

---

## Customizing the Scan

### Edit search queries (HF/GitHub)

Edit `scan-github-hf.py`:
- `GITHUB_QUERIES`: Array of GitHub search strings
- `HF_QUERIES`: Array of Hugging Face search keywords

Add queries like:
```python
"computer science education dataset",
"special education ai toolkit",
"multilingual classroom dataset"
```

### Edit monitor sources

Edit `data/source-watchlist.json` to add/remove sources:
```json
{
  "name": "Your New Source",
  "type": "Dataset repository",
  "mode": "monitor",
  "url": "https://example.org/datasets/",
  "keywords": ["k-12", "education", "dataset"]
}
```

---

## Accuracy & Quality

### Spot-Check Results (v18 Base Inventory)

20 randomly sampled records from your manually-verified v18:
- ✅ **20/20 links working** (100%)
- ✅ **All URLs current** (no redirects/changes)
- ✅ **Tier classifications accurate**

**Verdict:** Your v18 is **production-ready** and reliable.

### New Discoveries (from scanners)

New resources are marked **"Not Reviewed"** because:
- They haven't been manually verified yet
- GitHub/HF finds are not pre-audited (unlike your v18)
- Require quick spot-check before sharing

### Recommended verification workflow:

1. **Weekly auto-update runs** → finds new resources
2. **Team spot-checks** a sample (10-15 resources)
3. **Bulk review** filters by high-confidence criteria:
   - fit_score >= 70
   - From HF (more reliable than GitHub finds)
   - Has description text
4. **Tier assignment** once verified

---

## GitHub Pages Deployment

To share the live scanner with non-technical coworkers:

1. Go to repo **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: **main** → **Save**

Your site will be live at:
```
https://xweidp.github.io/k12-ai-scanner/
```

(In future, we'll build an interactive web interface for coworkers to browse the inventory.)

---

## Cost Analysis

**API Usage:**
- GitHub API: 60 requests/hour (unauthenticated) → plenty for weekly scan
- Hugging Face API: Free, no auth needed
- GitHub Actions: Free tier (2000 min/month) → 52 weeks of scans ✓

**Cost:** $0 / month

---

## Next Steps

### Short-term (next few weeks)
- Monitor auto-scans for quality
- Do spot-check verification of new resources
- Filter high-confidence records for team review
- Identify false positives and adjust queries

### Medium-term (2-3 months)
- Switch from Gemini to Claude for any LLM-based auditing
- Build interactive web interface for coworkers
- Create team review workflow
- Integrate v18 classifications into web interface

### Long-term (ongoing)
- Monthly or quarterly deep-dive reviews
- Update search queries based on new sources
- Maintain and extend monitor-source watchlist
- Track resource lifecycle (links break, licenses change, etc.)

---

## Monitoring the Workflow

Check scan status anytime:

**GitHub Actions tab:**
https://github.com/xweidp/k12-ai-scanner/actions

**Latest inventory:**
https://github.com/xweidp/k12-ai-scanner/blob/main/data/k12_inventory_latest.csv

**Discovery summary:**
https://github.com/xweidp/k12-ai-scanner/blob/main/data/discovery_summary.json
