import { mkdir, readFile, writeFile } from "node:fs/promises";

const SEARCH_QUERIES = [
  "K-12 education AI data learning research teacher technology",
  "education learning science artificial intelligence assessment accessibility",
  "teacher professional development STEM education workforce data",
  "education research public goods data infrastructure digital equity",
  "postsecondary student success higher education retention completion transfer",
  "postsecondary workforce career pathways adult learning competency-based education",
  "adult education workforce development career technical education credentials pathways",
  "community college workforce pathways undergraduate STEM education",
  "STEM education broadening participation undergraduate teacher pathways",
  "secondary data analysis education research longitudinal administrative data",
  "IES education research statistical analysis dataset longitudinal survey"
];

const PROFILE_TERMS = [
  "ai",
  "artificial intelligence",
  "machine learning",
  "data",
  "dataset",
  "metadata",
  "infrastructure",
  "public goods",
  "open",
  "privacy",
  "interoperability",
  "learning",
  "outcomes",
  "intervention",
  "evaluation",
  "evidence",
  "literacy",
  "assessment",
  "teacher",
  "educator",
  "workforce",
  "professional development",
  "implementation",
  "district",
  "equity",
  "accessibility",
  "disability",
  "multilingual",
  "rural",
  "stem",
  "k-12",
  "postsecondary",
  "higher education",
  "undergraduate",
  "community college",
  "student success",
  "career",
  "career pathways",
  "workforce development",
  "adult learning",
  "adult education",
  "adult learners",
  "competency-based education",
  "competency based education",
  "cbe",
  "credential",
  "credentials",
  "skills",
  "upskilling",
  "retention",
  "completion",
  "transfer",
  "credit accumulation",
  "advising",
  "basic needs",
  "trio",
  "hsi",
  "hbcu",
  "minority serving institution",
  "science",
  "technology",
  "engineering",
  "mathematics",
  "computer science",
  "cyber",
  "pathways",
  "broadening participation",
  "secondary data",
  "data analysis",
  "administrative data",
  "longitudinal",
  "restricted-use",
  "public-use",
  "survey",
  "nces",
  "ies",
  "ipeds",
  "statistical",
  "causal",
  "quasi-experimental",
  "replication"
];

const AGENCY_FILTER = "NSF|ED|DOL-OESE|DOL-OPE|HHS-ACF-OPRE";
const CATEGORY_FILTER = "ED|ST|ISS";
const GRANTS_API = "https://api.grants.gov/v1/api";
const WATCHLIST_PATH = "data/source-watchlist.json";

async function postJson(path, body) {
  const response = await fetch(`${GRANTS_API}/${path}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body)
  });

  if (!response.ok) {
    throw new Error(`${path} failed with ${response.status}`);
  }

  const json = await response.json();
  if (json.errorcode !== 0) {
    throw new Error(`${path} returned error: ${json.msg || "unknown error"}`);
  }
  return json.data;
}

async function searchOpportunities() {
  const byId = new Map();

  for (const keyword of SEARCH_QUERIES) {
    const data = await postJson("search2", {
      keyword,
      oppStatuses: "forecasted|posted",
      agencies: AGENCY_FILTER,
      fundingCategories: CATEGORY_FILTER,
      rows: 100,
      sortBy: "closeDate|asc"
    });

    for (const hit of data.oppHits || []) {
      byId.set(String(hit.id), hit);
    }
  }

  return [...byId.values()];
}

async function scanWatchlistSources() {
  const watchlist = await loadWatchlist();
  const leads = [];

  for (const source of watchlist.sources || []) {
    leads.push(...(await scanSourcePage(source)));
  }

  return dedupeByUrl(leads);
}

async function loadWatchlist() {
  try {
    return JSON.parse(await readFile(WATCHLIST_PATH, "utf8"));
  } catch {
    return { sources: [] };
  }
}

async function scanSourcePage(source) {
  try {
    const response = await fetch(source.url, {
      headers: {
        "user-agent": "EducationOpportunityScanner/1.0 (+https://github.com/xweidp/education-opportunity-scanner)"
      }
    });

    if (!response.ok) {
      throw new Error(`${source.url} returned ${response.status}`);
    }

    const html = await response.text();
    const pageText = cleanHtml(html).slice(0, 1200);
    const links = extractLinks(html, source.url)
      .filter((link) => isWatchlistLinkRelevant(link, source))
      .slice(0, 8);

    if (!links.length && isWatchlistTextRelevant(pageText, source)) {
      links.push({
        title: `${source.name} funding page`,
        url: source.url,
        text: pageText
      });
    }

    return links.map((link, index) => ({
      id: `watchlist-${source.name.toLowerCase().replace(/[^a-z0-9]+/g, "-")}-${index}`,
      number: "",
      title: link.title,
      source: source.name,
      sourceType: source.type,
      agencyCode: source.type,
      deadline: extractDeadline(`${link.title} ${link.text}`),
      posted: "",
      status: "watchlist",
      url: link.url,
      awardCeiling: "",
      estimatedFunding: "",
      eligibility: [],
      description: `${source.type}. Matched source page for ${source.name}. ${cleanHtml(link.text || pageText).slice(0, 700)}`
    }));
  } catch (error) {
    return [
      {
        id: `watchlist-${source.name.toLowerCase().replace(/[^a-z0-9]+/g, "-")}-source`,
        number: "",
        title: `${source.name} funding page`,
        source: source.name,
        sourceType: source.type,
        agencyCode: source.type,
        deadline: "",
        posted: "",
        status: "source-check",
        url: source.url,
        awardCeiling: "",
        estimatedFunding: "",
        eligibility: [],
        description: `${source.type}. Source page to monitor for education funding opportunities. The scan could not extract page details this run.`
      }
    ];
  }
}

function extractLinks(html, baseUrl) {
  const links = [];
  const linkPattern = /<a\b[^>]*href=["']([^"']+)["'][^>]*>([\s\S]*?)<\/a>/gi;
  let match;

  while ((match = linkPattern.exec(html))) {
    const url = normalizeUrl(match[1], baseUrl);
    const title = cleanHtml(match[2]);
    if (!url || !title || title.length < 3) continue;
    links.push({ title, url, text: title });
  }

  return dedupeByUrl(links);
}

function normalizeUrl(value, baseUrl) {
  try {
    return new URL(value, baseUrl).href;
  } catch {
    return "";
  }
}

function isWatchlistLinkRelevant(link, source) {
  const haystack = `${link.title} ${link.url}`.toLowerCase();
  const sourceKeywords = (source.keywords || []).some((keyword) => termMatches(haystack, keyword.toLowerCase()));
  const generalKeywords = /(grant|funding|rfp|rfa|opportunit|application|award|research|education|postsecondary|student|teacher|learning|stem|data|career|workforce|adult learning|adult education|pathways|credential|competency)/i.test(
    haystack
  );
  const skip =
    /(skip to|privacy|contact|newsletter|twitter|facebook|linkedin|instagram|youtube|donate|careers|staff|board|annual report|home$|accessibility)/i.test(
      haystack
    );
  return !skip && (sourceKeywords || generalKeywords);
}

function isWatchlistTextRelevant(text, source) {
  const haystack = `${source.name} ${source.type} ${text}`.toLowerCase();
  return (source.keywords || []).some((keyword) => termMatches(haystack, keyword.toLowerCase()));
}

function extractDeadline(text) {
  const match = String(text).match(
    /\b(20\d{2}[-/]\d{1,2}[-/]\d{1,2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+20\d{2})\b/i
  );
  return match ? normalizeDate(match[0]) : "";
}

function dedupeByUrl(items) {
  const seen = new Set();
  return items.filter((item) => {
    const key = item.url || item.id;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

async function fetchDetails(hit) {
  try {
    const data = await postJson("fetchOpportunity", { opportunityId: String(hit.id) });
    const synopsis = data.synopsis || {};
    const description = cleanHtml(synopsis.synopsisDesc || "");
    const url = synopsis.fundingDescLinkUrl || `https://www.grants.gov/search-results-detail/${hit.id}`;

    return {
      id: String(hit.id),
      number: data.opportunityNumber || hit.number || "",
      title: decodeEntities(data.opportunityTitle || hit.title || ""),
      source: decodeEntities(synopsis.agencyName || hit.agency || ""),
      agencyCode: synopsis.agencyCode || hit.agencyCode || "",
      deadline: normalizeDate(synopsis.responseDate || hit.closeDate || ""),
      posted: normalizeDate(synopsis.postingDate || hit.openDate || ""),
      status: hit.oppStatus || "",
      url,
      awardCeiling: normalizeMoney(synopsis.awardCeiling),
      estimatedFunding: normalizeMoney(synopsis.estimatedFunding),
      eligibility: (synopsis.applicantTypes || []).map((item) => item.description).filter(Boolean),
      description
    };
  } catch (error) {
    return {
      id: String(hit.id),
      number: hit.number || "",
      title: decodeEntities(hit.title || ""),
      source: decodeEntities(hit.agency || ""),
      agencyCode: hit.agencyCode || "",
      deadline: normalizeDate(hit.closeDate || ""),
      posted: normalizeDate(hit.openDate || ""),
      status: hit.oppStatus || "",
      url: `https://www.grants.gov/search-results-detail/${hit.id}`,
      awardCeiling: "",
      estimatedFunding: "",
      eligibility: [],
      description: ""
    };
  }
}

function scoreOpportunity(item) {
  const haystack = `${item.title} ${item.source} ${item.description}`.toLowerCase();
  const matched = PROFILE_TERMS.filter((term) => termMatches(haystack, term));
  const sourceBoost = /(nsf|national science foundation|department of education|institute of education sciences|opre|oese|ope)/i.test(
    `${item.source} ${item.agencyCode}`
  )
    ? 14
    : 0;
  const nonFederalBoost = /(private foundation|state funding)/i.test(`${item.sourceType || ""} ${item.agencyCode || ""}`) ? 8 : 0;
  const methodBoost = /(evaluation|randomized|evidence|implementation|assessment|data|infrastructure|technical assistance|professional development|secondary data|longitudinal|administrative data|statistical|quasi-experimental)/i.test(
    haystack
  )
    ? 14
    : 0;
  const digitalPromiseBoost = /(ai|artificial intelligence|learning science|digital|equity|accessibility|teacher|k-12|stem|postsecondary|higher education|student success|career|workforce|adult learning|pathways|competency-based|credential|data)/i.test(
    haystack
  )
    ? 12
    : 0;
  const urgentBoost = daysUntil(item.deadline) >= 0 && daysUntil(item.deadline) <= 30 ? 4 : 0;
  const focusBoost =
    /(education|student success|teacher|learning|professional development|workforce|career|pathways|adult learning|adult education|competency-based education|credential|broadening participation|assessment|secondary data|postsecondary|higher education|undergraduate|community college)/i.test(
      haystack
    )
      ? 12
      : 0;
  const weakStemPenalty =
    /(anthropology|astronomy|biology|chemistry|physics|plasma|oceanographic|arctic|mathematical sciences|social psychology|developmental sciences)/i.test(
      haystack
    ) && !/(education|student|teacher|learning|workforce|career|pathways|adult learning|adult education|credential|competency|postsecondary|undergraduate|community college|secondary data|assessment)/i.test(haystack)
      ? 28
      : 0;
  const fit = Math.min(
    100,
    Math.max(
      0,
      Math.round(18 + matched.length * 4 + sourceBoost + nonFederalBoost + methodBoost + digitalPromiseBoost + focusBoost + urgentBoost - weakStemPenalty)
    )
  );

  return {
    ...item,
    fit,
    matchedTerms: matched.slice(0, 8)
  };
}

function isRelevant(item) {
  const title = `${item.title}`.toLowerCase();
  const haystack = `${item.title} ${item.source} ${item.description}`.toLowerCase();
  const educationFocus = /(education|teacher|educator|learning|student|school|assessment|literacy|postsecondary|higher education|undergraduate|community college|student success|retention|completion|transfer|professional development|workforce|career|pathways|adult learning|adult education|credential|competency|broadening participation|secondary data|administrative data|longitudinal|nces|ies|ipeds)/i;
  const weakDisciplineOnly = /(arctic|astronomy|biology|chemistry|physics|plasma|oceanographic|anthropology|mathematical biology|geometric|topology|forensics|defense|naval|brain initiative|social psychology|developmental sciences)/i;
  if (weakDisciplineOnly.test(haystack) && !educationFocus.test(haystack)) {
    return false;
  }
  if (weakDisciplineOnly.test(title) && !/(education|teacher|educator|learning|student|school|postsecondary|undergraduate|community college|workforce|career|pathways|adult learning|credential|competency|assessment|secondary data)/i.test(title)) {
    return false;
  }
  return /(education|teacher|learning|student|school|stem education|assessment|literacy|accessibility|artificial intelligence education|ai education|workforce|career|pathways|adult learning|adult education|credential|competency|professional development|postsecondary|higher education|undergraduate|community college|secondary data|longitudinal|administrative data|student success|broadening participation)/i.test(
    haystack
  );
}

function termMatches(haystack, term) {
  const escaped = term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const shortOrAcronym = term.length <= 4 || term === term.toUpperCase();
  const pattern = shortOrAcronym ? `\\b${escaped}\\b` : `(^|[^a-z0-9])${escaped}([^a-z0-9]|$)`;
  return new RegExp(pattern, "i").test(haystack);
}

function cleanHtml(value) {
  return decodeEntities(
    String(value)
      .replace(/<[^>]+>/g, " ")
      .replace(/\s+/g, " ")
      .trim()
  );
}

function decodeEntities(value) {
  return String(value)
    .replace(/&amp;/g, "&")
    .replace(/&nbsp;/g, " ")
    .replace(/&#8209;/g, "-")
    .replace(/&ndash;/g, "-")
    .replace(/&mdash;/g, "-")
    .replace(/&rsquo;/g, "'")
    .replace(/&ldquo;/g, '"')
    .replace(/&rdquo;/g, '"')
    .replace(/\s+/g, " ")
    .trim();
}

function normalizeDate(value) {
  if (!value) return "";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return "";
  return parsed.toISOString().slice(0, 10);
}

function normalizeMoney(value) {
  if (!value || value === "none") return "";
  const number = Number(value);
  if (!Number.isFinite(number) || number <= 0) return "";
  return String(number);
}

function daysUntil(deadline) {
  if (!deadline) return Number.POSITIVE_INFINITY;
  const date = new Date(`${deadline}T23:59:59Z`);
  if (Number.isNaN(date.getTime())) return Number.POSITIVE_INFINITY;
  const today = new Date();
  today.setUTCHours(0, 0, 0, 0);
  return Math.ceil((date - today) / 86400000);
}

function csvEscape(value) {
  return `"${String(value ?? "").replaceAll('"', '""')}"`;
}

function makeCsv(items) {
  const header = ["title", "source", "source_type", "deadline", "fit", "number", "url", "matched_terms", "description"];
  const rows = items.map((item) => [
    item.title,
    item.source,
    item.sourceType || "",
    item.deadline,
    item.fit,
    item.number,
    item.url,
    item.matchedTerms.join("; "),
    item.description
  ]);
  return [header, ...rows].map((row) => row.map(csvEscape).join(",")).join("\n");
}

function makeBrief(items, scannedAt) {
  const top = items.slice(0, 15);
  const lines = [
    "# Weekly Education Research Opportunity Scan",
    "",
    `Scanned at: ${scannedAt}`,
    "",
    "## Top Matches",
    ""
  ];

  top.forEach((item, index) => {
    lines.push(`${index + 1}. ${item.title}`);
    lines.push(`   Deadline: ${item.deadline || "Not listed"} | Fit: ${item.fit} | Source: ${item.source}`);
    lines.push(`   Terms: ${item.matchedTerms.join(", ") || "education relevance"}`);
    lines.push(`   Link: ${item.url}`);
    lines.push("");
  });

  return lines.join("\n");
}

async function main() {
  const hits = await searchOpportunities();
  const detailed = [];

  for (const hit of hits) {
    detailed.push(await fetchDetails(hit));
  }

  const watchlistLeads = await scanWatchlistSources();

  const federalOpportunities = detailed
    .filter(isRelevant)
    .map(scoreOpportunity)
    .filter((item) => !item.deadline || daysUntil(item.deadline) >= -3)
    .sort((a, b) => daysUntil(a.deadline) - daysUntil(b.deadline) || b.fit - a.fit)
    .slice(0, 60);

  const sourceWatchlistOpportunities = watchlistLeads
    .filter(isRelevant)
    .map(scoreOpportunity)
    .sort((a, b) => daysUntil(a.deadline) - daysUntil(b.deadline) || b.fit - a.fit)
    .slice(0, 30);

  const opportunities = [...federalOpportunities, ...sourceWatchlistOpportunities].sort(
    (a, b) => daysUntil(a.deadline) - daysUntil(b.deadline) || b.fit - a.fit
  );

  const scannedAt = new Date().toISOString();
  const payload = {
    scannedAt,
    source: "Grants.gov API + private/state source watchlist",
    profile: "Digital Promise + education AI/data/learning-sciences fit",
    opportunities
  };

  await mkdir("data", { recursive: true });
  await writeFile("data/opportunities.json", `${JSON.stringify(payload, null, 2)}\n`);
  await writeFile("data/weekly_opportunities.csv", `${makeCsv(opportunities)}\n`);
  await writeFile("weekly_opportunity_brief.md", makeBrief(opportunities, scannedAt));

  console.log(`Wrote ${opportunities.length} opportunities.`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
