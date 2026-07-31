# Weekly Auto-Scan Setup

This project is ready for a weekly auto-refresh using GitHub Actions plus Netlify.

## How It Works

1. GitHub Actions runs `.github/workflows/weekly-scan.yml` every Monday (default time).
2. The workflow runs `node scripts/scan-resources.mjs`.
3. The script:
   - Fetches the K-12 AI Infrastructure Platform catalog (structured parsing)
   - Monitors DrivenData, Learning Commons, Hugging Face, and other resource hubs
   - Scores and ranks resources by K-12 relevance
4. It writes:
   - `data/resources.json` — Full resource records with metadata
   - `data/weekly_resources.csv` — Exportable spreadsheet format
   - `weekly_resource_brief.md` — Human-readable summary of top resources
5. The workflow commits those files.
6. Netlify sees the GitHub commit and automatically redeploys the app.

## One-Time Setup

1. Create a GitHub repository.
2. Add the contents of `/Users/xinwei/Documents/Projects/K12AI/Scanner` to that repository.
3. Push to GitHub.
4. In Netlify, choose **Add new site** and connect the GitHub repository.
5. Use these Netlify build settings:
   - Build command: leave blank
   - Publish directory: `.`
6. (Optional) Turn on Netlify password protection if the data is not public.
7. In GitHub, open the repository's **Actions** tab and make sure workflows are enabled.
8. Copy `.github/workflows/weekly-scan.yml` from `netlify_upload/` to your repo.

## Schedule

The workflow currently runs at:

```yaml
0 13 * * 1
```

That is Monday 8:00 AM Central during daylight saving time. During standard time, 8:00 AM Central is:

```yaml
0 14 * * 1
```

Edit the cron schedule in `.github/workflows/weekly-scan.yml` to change the time. You can also run it manually from GitHub Actions with **Run workflow**.

## Local Test

Run the scanner:

```bash
node scripts/scan-resources.mjs
```

Then preview the app:

```bash
python3 -m http.server 8766
```

Open:

```text
http://localhost:8766
```

The app will load `data/resources.json` and display the scanned resources with filters and search.

