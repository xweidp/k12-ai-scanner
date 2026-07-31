# Cloudflare Pages Auto-Scan Setup

Deploy the K-12 AI Resource Scanner to Cloudflare Pages with automatic weekly scans.

## One-Time Setup

### 1. Connect GitHub to Cloudflare Pages

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Select **Pages** → **Create project** → **Connect to Git**
3. Authorize Cloudflare to access your GitHub account
4. Select the repository with the K-12 AI Scanner code
5. Click **Begin setup**

### 2. Configure Build Settings

- **Framework preset**: None
- **Build command**: Leave blank (no build step needed)
- **Build output directory**: `/` (root)
- **Environment variables**: (none required)

Click **Save and deploy**.

### 3. Enable Cron Triggers

Cron Triggers are a **Cloudflare Pages Function feature** that runs code on a schedule.

1. In your Pages project, go to **Settings** → **Functions** → **Cron Triggers**
2. Add this cron expression: `0 13 * * 1`
   - Runs every Monday at 1:00 PM UTC (8:00 AM Central)
   - Adjust the time zone if needed (see below)
3. Click **Save**

The `functions/scan-schedule.js` function will execute automatically.

## How It Works

1. **Cloudflare Pages** detects the cron trigger on Monday
2. **`functions/scan-schedule.js`** executes and:
   - Runs `node scripts/scan-resources.mjs` to fetch and score resources
   - Commits results to GitHub (via GitHub API + token)
3. **GitHub sees the commit** and webhooks Cloudflare Pages
4. **Cloudflare Pages redeploys** with fresh data
5. The live scanner shows the latest K-12 resources

## Cron Schedule Reference

The cron expression `0 13 * * 1` means:

```
 ┌───────────── minute (0 - 59)
 │ ┌───────────── hour (0 - 23)
 │ │ ┌───────────── day of month (1 - 31)
 │ │ │ ┌───────────── month (1 - 12)
 │ │ │ │ ┌───────────── day of week (0 - 6, 0 = Sunday)
 │ │ │ │ │
 0 13 * * 1
```

**Common schedules:**
- `0 13 * * 1` — Monday 1:00 PM UTC (8:00 AM Central)
- `0 9 * * 1` — Monday 9:00 AM UTC (4:00 AM Central)
- `0 0 * * 1` — Monday 12:00 AM UTC (7:00 PM Sunday Central)

## Setting Up GitHub Commit Access

The scan function needs to commit results back to GitHub. Set up a GitHub token:

1. Go to [GitHub Settings](https://github.com/settings/tokens) → **Personal access tokens** → **Tokens (classic)**
2. Click **Generate new token (classic)**
3. Name: `Cloudflare K12 Scanner`
4. Scopes: `repo` (full control of private repositories)
5. Click **Generate token** and copy the token
6. In Cloudflare Pages project settings:
   - Go to **Environment variables** → **Production**
   - Add variable: `GITHUB_TOKEN = <your-token>`

The scan function can then use `process.env.GITHUB_TOKEN` to authenticate commits.

## Advanced: Running the Full Scan

To run the complete scan (not just a trigger test), update `functions/scan-schedule.js`:

```javascript
// Install wrangler and run locally first:
// npm install wrangler
// wrangler pages functions build

// Then deploy to Cloudflare Pages
```

For production, you may want to:
1. Use a **GitHub Action** to run the full scan on schedule (instead of Cloudflare)
2. Commit results to GitHub
3. Cloudflare Pages auto-redeploys on GitHub webhook

This hybrid approach is more reliable for long-running scans.

## Monitoring

Check scan executions:
1. Cloudflare Pages project → **Deployments** tab
2. Look for deployments triggered on Mondays
3. Check function logs: **Settings** → **Functions** → **Logs**

## Troubleshooting

- **Cron not running?** Verify cron expression in **Settings** → **Functions** → **Cron Triggers**
- **Commit failed?** Check that `GITHUB_TOKEN` is set and has `repo` scope
- **Data not updating?** Verify `data/resources.json` was committed by checking GitHub repo
- **Time zone mismatch?** Cloudflare cron runs in UTC; adjust the expression if needed

## See Also

- [Cloudflare Pages Functions](https://developers.cloudflare.com/pages/platform/functions/)
- [Cron Triggers Documentation](https://developers.cloudflare.com/pages/platform/functions/scheduled-functions/)
