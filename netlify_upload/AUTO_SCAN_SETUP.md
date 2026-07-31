# Monday Auto-Scan Setup

This project is ready for a weekly auto-refresh using GitHub Actions plus Netlify.

## How It Works

1. GitHub Actions runs `.github/workflows/weekly-scan.yml` every Monday.
2. The workflow runs `node scripts/scan-opportunities.mjs`.
3. The script searches Grants.gov for education research opportunities.
4. It writes:
   - `data/opportunities.json`
   - `data/weekly_opportunities.csv`
   - `weekly_opportunity_brief.md`
5. The workflow commits those files.
6. Netlify sees the GitHub commit and automatically redeploys the password-protected app.

## One-Time Setup

1. Create a GitHub repository.
2. Add the contents of `/Users/xinwei/Desktop/Education Proposal` to that repository.
3. Push to GitHub.
4. In Netlify, choose **Add new site** and connect the GitHub repository.
5. Use these Netlify build settings:
   - Build command: leave blank
   - Publish directory: `.`
6. Turn on Netlify password protection in the site settings.
7. In GitHub, open the repository's **Actions** tab and make sure workflows are enabled.

## Schedule

The workflow currently runs at:

```yaml
0 13 * * 1
```

That is Monday 8:00 AM Central during daylight saving time. During standard time, 8:00 AM Central is:

```yaml
0 14 * * 1
```

You can also run it manually from GitHub Actions with **Run workflow**.

## Local Test

Run:

```bash
node scripts/scan-opportunities.mjs
```

Then preview the app:

```bash
python3 -m http.server 8766
```

Open:

```text
http://localhost:8766
```

