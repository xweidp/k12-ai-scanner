import { mkdir, readFile, writeFile } from "node:fs/promises";

// K-12 AI resource scanner.
//
// Unlike the funding scanner this is based on, there is no single API for
// education datasets/benchmarks/models. Instead we scan a watchlist of
// resource catalogs and hubs:
//   - "catalog" sources are parsed with a source-specific parser that pulls
//     structured metadata (title, host, subject, modality, license).
//   - "monitor" sources use best-effort link extraction and are surfaced as
//     leads to review.
//
// Output: data/resources.json, data/weekly_resources.csv, weekly_resource_brief.md

const WATCHLIST_PATH = "data/source-watchlist.json";
const USER_AGENT = "K12ResourceScanner/1.0 (K-12 AI Infrastructure Program dataset/benchmark/model scan)";

// Relevance vocabulary for K-12 AI datasets, benchmarks, and models.
const PROFILE_TERMS = [
  "dataset", "benchmark", "model", "corpus", "annotated", "labeled",
  "ai", "artificial intelligence", "machine learning", "llm", "language model",
  "nlp", "evaluation", "eval", "leaderboard", "fine-tune",
  "k-12", "elementary", "middle school", "high school", "grade school", "classroom",
  "student", "teacher", "tutoring", "tutor", "instruction", "curriculum", "standards",
  "math", "mathematics", "word problem", "reasoning", "arithmetic",
  "science", "reading", "literacy", "writing", "essay", "argumentative", "narrative",
  "assessment", "grading", "scoring", "rubric", "short-answer", "multiple-choice",
  "question answering", "qa", "dialogue", "transcript", "discourse",
  "learning science", "knowledge graph", "accessibility", "equity", "multilingual",
  "english learner", "special education", "education"
];

// Subject taxonomy for tagging.
const SUBJECT_TERMS = {
  Math: ["math", "mathematics", "arithmetic", "word problem", "gsm", "algebra", "geometry", "numeric"],
  Science: ["science", "scientific", "physics", "chemistry", "biology", "sciq"],
  Reading: ["reading", "comprehension", "fairytale", "narrative"],
  Writing: ["writing", "essay", "argumentative", "lexical"],
  Literacy: ["literacy"],
  Tutoring: ["tutoring", "tutor", "dialogue"],
  Assessment: ["assessment", "grading", "scoring", "rubric", "graded", "mistake"],
  "Classroom discourse": ["classroom", "transcript", "discursive", "talk moves", "discourse"]
};

// Known data modalities used as chip labels on catalog pages.
const MODALITY_TERMS = [
  "tabular", "image", "text", "human transcript", "transcript", "audio", "video",
  "time series", "geospatial", "genomic", "multimodal", "code", "graph", "handwriting"
];

// -------------------------------------------------------------------------
// Fetch + HTML helpers
// -------------------------------------------------------------------------

async function fetchHtml(url) {
  const response = await fetch(url, { headers: { "user-agent": USER_AGENT } });
  if (!response.ok) throw new Error(`${url} returned ${response.status}`);
  return response.text();
}

function decodeEntities(value) {
  return String(value)
    .replace(/&amp;/g, "&")
    .replace(/&nbsp;/g, " ")
    .replace(/&#8209;/g, "-")
    .replace(/&ndash;|&mdash;|&#8211;|&#8212;/g, "-")
    .replace(/&rsquo;|&#8217;/g, "'")
    .replace(/&lsquo;|&#8216;/g, "'")
    .replace(/&ldquo;|&rdquo;|&#8220;|&#8221;/g, '"')
    .replace(/&hellip;/g, "...")
    .replace(/&#(\d+);/g, (_, n) => String.fromCharCode(Number(n)))
    .replace(/\s+/g, " ")
    .trim();
}

function cleanHtml(value) {
  return decodeEntities(String(value).replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim());
}

function normalizeUrl(value, baseUrl) {
  try {
    return new URL(value, baseUrl).href;
  } catch {
    return "";
  }
}

function termMatches(haystack, term) {
  const escaped = term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const shortOrAcronym = term.length <= 3 || term === term.toUpperCase();
  const pattern = shortOrAcronym ? `\\b${escaped}\\b` : `(^|[^a-z0-9])${escaped}([^a-z0-9]|$)`;
  return new RegExp(pattern, "i").test(haystack);
}

// -------------------------------------------------------------------------
// Classification + tagging
// -------------------------------------------------------------------------

function classifyResourceType(text, hintChips = []) {
  const haystack = `${text} ${hintChips.join(" ")}`.toLowerCase();
  if (/\b(model|llm|fine-?tuned?|checkpoint|pretrained|pre-trained|weights)\b/.test(haystack)) {
    return "Model";
  }
  if (/\b(benchmark|bench\b|leaderboard|eval\b|evaluation set|multiple-choice|graded responses|test set)\b/.test(haystack) ||
      /bench\b/i.test(text)) {
    return "Benchmark";
  }
  if (/\b(competition|challenge)\b/.test(haystack)) {
    return "Competition";
  }
  return "Dataset";
}

function detectSubjects(text) {
  const haystack = text.toLowerCase();
  const subjects = [];
  for (const [subject, terms] of Object.entries(SUBJECT_TERMS)) {
    if (terms.some((term) => termMatches(haystack, term))) subjects.push(subject);
  }
  return [...new Set(subjects)];
}

function detectGradeBand(text) {
  const haystack = text.toLowerCase();
  if (/\b(grade school|grade-school|elementary|primary school)\b/.test(haystack)) return "Elementary";
  if (/\bmiddle school\b/.test(haystack)) return "Middle school";
  if (/\bhigh school\b/.test(haystack)) return "High school";
  if (/\bk-?12\b/.test(haystack)) return "K-12";
  return "K-12 (unspecified)";
}

function bucketChips(chips) {
  const modality = [];
  const subjectChips = [];
  let license = "";
  for (const raw of chips) {
    const chip = raw.trim();
    if (!chip) continue;
    if (/^(cc[ 0-]|cc-by|cc0|mit|apache|bsd|gpl|odc|odbl|public domain|proprietary|custom license|other license|unknown license)/i.test(chip) ||
        /\blicense\b/i.test(chip)) {
      if (!license) license = chip;
      continue;
    }
    if (MODALITY_TERMS.some((m) => chip.toLowerCase() === m || chip.toLowerCase().includes(m))) {
      modality.push(chip);
      continue;
    }
    subjectChips.push(chip);
  }
  return { modality: [...new Set(modality)], subjectChips: [...new Set(subjectChips)], license };
}

// -------------------------------------------------------------------------
// Catalog parser: K-12 AI Infrastructure Program dataset cards
// -------------------------------------------------------------------------

function parseKaiipCatalog(html, source) {
  const cards = html.split(/<div class="d-flex col-md-6 col-xl-4 panel-container/i).slice(1);
  const records = [];

  cards.forEach((card, index) => {
    const linkMatch = card.match(/href='(\/datasets\/\d+\/[^']+\/version\/\d+\/)'/i);
    const titleMatch = card.match(/panel-competition-title[^>]*>\s*([\s\S]*?)\s*<\/h3>/i);
    if (!linkMatch || !titleMatch) return;

    const url = normalizeUrl(linkMatch[1], source.url);
    const title = cleanHtml(titleMatch[1]);

    const orgMatch =
      card.match(/class="attribution-short"[^>]*>\s*([\s\S]*?)\s*<\/a>/i) ||
      card.match(/alt="Hosted by ([^"]+)"/i);
    const org = orgMatch ? cleanHtml(orgMatch[1]) : source.name;

    const descMatch = card.match(/<p class="mt-0 mb-2 color-body">\s*([\s\S]*?)\s*<\/p>/i);
    const description = descMatch ? cleanHtml(descMatch[1]) : "";

    // Metric chips (subject / modality / license).
    const chips = [];
    const chipPattern = /rounded-4[^>]*>[\s\S]*?<\/svg>\s*<\/div>\s*([^<]+?)\s*<\/div>/gi;
    let chipMatch;
    while ((chipMatch = chipPattern.exec(card))) {
      const label = cleanHtml(chipMatch[1]);
      if (label) chips.push(label);
    }
    const { modality, subjectChips, license } = bucketChips(chips);

    const context = `${title} ${description} ${subjectChips.join(" ")}`;
    const subjects = [...new Set([...subjectChips, ...detectSubjects(context)])];

    records.push({
      id: `kaiip-${(url.match(/datasets\/(\d+)/) || [])[1] || index}`,
      title,
      source: org,
      program: source.name,
      sourceType: source.type,
      resourceType: classifyResourceType(context, chips),
      url,
      subjects,
      gradeBand: detectGradeBand(context),
      modality,
      license: license || "See dataset page",
      description,
      addedVia: "catalog"
    });
  });

  return records;
}

// -------------------------------------------------------------------------
// Monitor parser: best-effort link extraction for hubs / news pages
// -------------------------------------------------------------------------

const SKIP_LINK = /(skip to|sign in|log in|register|privacy|terms|cookie|contact|newsletter|subscribe|twitter|facebook|linkedin|instagram|youtube|github\.com\/[^/]+$|donate|careers|about us|home$|menu|search$|previous|next|©|all rights)/i;

function parseMonitorSource(html, source) {
  const links = [];
  const linkPattern = /<a\b[^>]*href=["']([^"']+)["'][^>]*>([\s\S]*?)<\/a>/gi;
  const patternRe = source.linkPattern ? new RegExp(source.linkPattern, "i") : null;
  const seen = new Set();
  let match;

  while ((match = linkPattern.exec(html))) {
    const rawHref = match[1];
    const title = cleanHtml(match[2]);
    const url = normalizeUrl(rawHref, source.url);
    if (!url || !title || title.length < 4) continue;
    const haystack = `${title} ${rawHref}`.toLowerCase();

    if (SKIP_LINK.test(haystack)) continue;
    if (patternRe && !patternRe.test(rawHref)) continue;

    const keywordHit = (source.keywords || []).some((kw) => termMatches(haystack, kw.toLowerCase()));
    if (!patternRe && !keywordHit) continue;

    if (seen.has(url)) continue;
    seen.add(url);

    const context = `${title} ${source.name}`;
    links.push({
      id: `monitor-${source.name.toLowerCase().replace(/[^a-z0-9]+/g, "-")}-${links.length}`,
      title,
      source: source.name,
      program: source.name,
      sourceType: source.type,
      resourceType: classifyResourceType(`${context} ${rawHref}`),
      url,
      subjects: detectSubjects(context),
      gradeBand: detectGradeBand(context),
      modality: [],
      license: "See source",
      description: `${source.type} lead from ${source.name}. Review the linked page for dataset/benchmark/model details.`,
      addedVia: "monitor"
    });

    if (links.length >= 25) break;
  }

  return links;
}

// -------------------------------------------------------------------------
// Scoring
// -------------------------------------------------------------------------

function scoreResource(item) {
  const haystack = `${item.title} ${item.source} ${item.description} ${item.subjects.join(" ")} ${item.modality.join(" ")}`.toLowerCase();
  const matched = PROFILE_TERMS.filter((term) => termMatches(haystack, term));

  const catalogBoost = item.addedVia === "catalog" ? 18 : 0;
  const k12Boost = /(k-?12|grade school|elementary|middle school|high school|classroom|student|teacher)/i.test(haystack) ? 14 : 0;
  const subjectBoost = item.subjects.length ? 10 : 0;
  const metadataBoost = (item.modality.length ? 6 : 0) + (item.license && !/^see /i.test(item.license) ? 6 : 0);
  const typeBoost = /(dataset|benchmark|model|corpus)/i.test(haystack) ? 8 : 0;

  const fit = Math.min(100, Math.max(0, Math.round(20 + matched.length * 3 + catalogBoost + k12Boost + subjectBoost + metadataBoost + typeBoost)));

  return { ...item, matchedTerms: matched.slice(0, 8), fit };
}

function isRelevant(item) {
  if (item.addedVia === "catalog") return true;
  const haystack = `${item.title} ${item.description} ${item.subjects.join(" ")}`.toLowerCase();
  return /(dataset|benchmark|model|corpus|education|learning|student|teacher|classroom|math|science|reading|literacy|assessment|tutoring|k-?12)/i.test(haystack);
}

function dedupe(items) {
  const seen = new Set();
  return items.filter((item) => {
    const key = item.url || item.id;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

// -------------------------------------------------------------------------
// Output writers
// -------------------------------------------------------------------------

function csvEscape(value) {
  return `"${String(value ?? "").replaceAll('"', '""')}"`;
}

function makeCsv(items) {
  const header = [
    "title", "resource_type", "source", "program", "source_type",
    "subjects", "grade_band", "modality", "license", "fit", "url", "matched_terms", "description"
  ];
  const rows = items.map((item) => [
    item.title,
    item.resourceType,
    item.source,
    item.program,
    item.sourceType,
    (item.subjects || []).join("; "),
    item.gradeBand,
    (item.modality || []).join("; "),
    item.license,
    item.fit,
    item.url,
    (item.matchedTerms || []).join("; "),
    item.description
  ]);
  return [header, ...rows].map((row) => row.map(csvEscape).join(",")).join("\n");
}

function makeBrief(items, scannedAt) {
  const top = items.slice(0, 20);
  const lines = [
    "# Weekly K-12 AI Resource Scan",
    "",
    `Scanned at: ${scannedAt}`,
    `Resources found: ${items.length}`,
    "",
    "## Top Matches",
    ""
  ];
  top.forEach((item, index) => {
    lines.push(`${index + 1}. ${item.title} — ${item.resourceType}`);
    lines.push(`   Source: ${item.source} | Fit: ${item.fit} | Grade: ${item.gradeBand}`);
    lines.push(`   Subjects: ${(item.subjects || []).join(", ") || "Not tagged"} | Modality: ${(item.modality || []).join(", ") || "Not listed"} | License: ${item.license}`);
    lines.push(`   ${item.description}`);
    lines.push(`   Link: ${item.url}`);
    lines.push("");
  });
  return lines.join("\n");
}

// -------------------------------------------------------------------------
// Main
// -------------------------------------------------------------------------

async function loadWatchlist() {
  try {
    return JSON.parse(await readFile(WATCHLIST_PATH, "utf8"));
  } catch {
    return { sources: [] };
  }
}

async function scanSource(source) {
  try {
    const html = await fetchHtml(source.url);
    if (source.mode === "catalog" && source.parser === "kaiip") {
      return parseKaiipCatalog(html, source);
    }
    return parseMonitorSource(html, source);
  } catch (error) {
    console.warn(`  ! ${source.name}: ${error.message}`);
    return [];
  }
}

async function main() {
  const watchlist = await loadWatchlist();
  const collected = [];

  for (const source of watchlist.sources || []) {
    process.stdout.write(`Scanning ${source.name} ...\n`);
    const found = await scanSource(source);
    console.log(`  -> ${found.length} items`);
    collected.push(...found);
  }

  const resources = dedupe(collected)
    .filter(isRelevant)
    .map(scoreResource)
    .sort((a, b) => b.fit - a.fit || a.title.localeCompare(b.title));

  const scannedAt = new Date().toISOString();
  const payload = {
    scannedAt,
    source: "K-12 AI resource watchlist (catalogs + hubs)",
    profile: "K-12 AI datasets, benchmarks, and models",
    counts: {
      total: resources.length,
      datasets: resources.filter((r) => r.resourceType === "Dataset").length,
      benchmarks: resources.filter((r) => r.resourceType === "Benchmark").length,
      models: resources.filter((r) => r.resourceType === "Model").length,
      competitions: resources.filter((r) => r.resourceType === "Competition").length
    },
    resources
  };

  await mkdir("data", { recursive: true });
  await writeFile("data/resources.json", `${JSON.stringify(payload, null, 2)}\n`);
  await writeFile("data/weekly_resources.csv", `${makeCsv(resources)}\n`);
  await writeFile("weekly_resource_brief.md", makeBrief(resources, scannedAt));

  console.log(`\nWrote ${resources.length} resources (${payload.counts.datasets} datasets, ${payload.counts.benchmarks} benchmarks, ${payload.counts.models} models, ${payload.counts.competitions} competitions).`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
