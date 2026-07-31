# Netlify Deployment Notes

Best option for coworkers: deploy the app as a static Netlify site connected to GitHub, then use Netlify's built-in Password Protection from the Netlify UI. That keeps the shared password out of this project folder and lets GitHub Actions refresh the opportunity list every Monday.

## Recommended Password Setup

Use Netlify's **Password Protection** setting if your team has a Netlify Pro plan:

1. Upload or connect this folder as a Netlify site.
2. In Netlify, open the site dashboard.
3. Go to **Site configuration** or **Security**.
4. Find **Password Protection** or **Visitor access**.
5. Choose **Basic password protection**.
6. Protect **all deploys**.
7. Set one shared password for coworkers.

Netlify's docs say basic password protection for an entire site is available on Pro plans. Enterprise plans add more login-control options.

## Alternative: Basic Auth Header

If you prefer file-based protection, copy `_headers.example` to `_headers`, replace the placeholder password, and deploy. This also requires Netlify Pro or Enterprise.

Do not use a password you use anywhere else. The `_headers` method stores the shared password in the deploy files, so Netlify UI password protection is cleaner.

## Deploy Method

The app is static. No build step is required.

For the weekly auto-scan, use Git deploy:

1. Put `/Users/xinwei/Desktop/Education Proposal` in a GitHub repository.
2. Connect the repo in Netlify.
3. Build command: leave blank.
4. Publish directory: `.`
5. Keep GitHub Actions enabled.

The included workflow at `.github/workflows/weekly-scan.yml` runs every Monday morning, updates `data/opportunities.json`, commits it, and lets Netlify redeploy automatically.

For drag-and-drop deploy without auto-refresh:

1. Open Netlify.
2. Choose **Add new site**.
3. Choose **Deploy manually**.
4. Drag the `/Users/xinwei/Desktop/Education Proposal` folder into Netlify.

Drag-and-drop is fine for a static snapshot, but it will not run the Monday auto-scan.

## Files Netlify Needs

- `index.html`
- `styles.css`
- `app.js`
- `netlify.toml`
- optional `_headers`
- `data/opportunities.json`
- `scripts/scan-opportunities.mjs`
- `.github/workflows/weekly-scan.yml` for GitHub auto-refresh
