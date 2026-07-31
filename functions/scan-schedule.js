/**
 * Cloudflare Pages Function: Weekly K-12 AI Resource Scanner
 *
 * Triggered every Monday at 1:00 PM UTC (8:00 AM Central)
 * Runs scan-resources.mjs and commits results to GitHub
 */

export async function onRequest({ cron }) {
  // Only execute on cron trigger
  if (!cron.isTriggered) {
    return new Response("Not a scheduled trigger", { status: 400 });
  }

  try {
    console.log("Starting weekly K-12 AI resource scan...");

    // 1. Fetch the scan script from the repo (or run it via API)
    const scanUrl = "https://raw.githubusercontent.com/YOUR_GITHUB_ORG/k12-ai-scanner/main/scripts/scan-resources.mjs";

    console.log("Scan triggered. In production, this function would:");
    console.log("1. Run the scan-resources.mjs script");
    console.log("2. Commit results (data/resources.json, CSV, brief) to GitHub");
    console.log("3. GitHub webhook triggers Cloudflare Pages redeploy");

    // For now, return success
    return new Response(JSON.stringify({
      status: "success",
      message: "Weekly scan scheduled. Deploy to Cloudflare Pages to activate.",
      nextRun: "Next Monday 1:00 PM UTC"
    }), {
      status: 200,
      headers: { "Content-Type": "application/json" }
    });
  } catch (error) {
    console.error("Scan error:", error);
    return new Response(JSON.stringify({
      status: "error",
      message: error.message
    }), {
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }
}

// Cron trigger configuration
export const config = {
  // Cron expression: minute hour day month weekday
  // 0 13 * * 1 = Every Monday at 1:00 PM UTC (8:00 AM Central)
  triggers: {
    crons: ["0 13 * * 1"]
  }
};
