const profiles = {
  all: [],
  ai: [
    "ai",
    "artificial intelligence",
    "machine learning",
    "data",
    "dataset",
    "metadata",
    "infrastructure",
    "public goods",
    "open science",
    "privacy",
    "interoperability"
  ],
  learning: [
    "learning",
    "outcomes",
    "intervention",
    "randomized",
    "evaluation",
    "evidence",
    "math",
    "literacy",
    "assessment",
    "tutoring"
  ],
  equity: [
    "equity",
    "access",
    "rural",
    "multilingual",
    "english learner",
    "disability",
    "inclusive",
    "underserved",
    "community"
  ],
  workforce: [
    "teacher",
    "educator",
    "workforce",
    "professional learning",
    "implementation",
    "district",
    "school leader",
    "coaching",
    "retention"
  ],
  postsecondary: [
    "postsecondary",
    "higher education",
    "undergraduate",
    "college",
    "university",
    "community college",
    "student success",
    "persistence",
    "career",
    "career pathways",
    "workforce",
    "workforce development",
    "adult learning",
    "adult learners",
    "adult education",
    "pathways",
    "career pathways",
    "competency-based education",
    "competency based education",
    "cbe",
    "credentials",
    "credential",
    "skills",
    "upskilling",
    "retention",
    "completion",
    "transfer",
    "credit accumulation",
    "advising",
    "basic needs",
    "trio",
    "minority serving institution",
    "hsi",
    "hbcu"
  ],
  stem: [
    "stem",
    "science",
    "technology",
    "engineering",
    "mathematics",
    "computer science",
    "cs",
    "cyber",
    "ai",
    "workforce",
    "teacher",
    "pathways",
    "broadening participation",
    "undergraduate",
    "k-12"
  ],
  secondaryData: [
    "secondary data",
    "data analysis",
    "administrative data",
    "longitudinal",
    "restricted-use",
    "public-use",
    "dataset",
    "survey",
    "nces",
    "ies",
    "ipeds",
    "els",
    "hsls",
    "statistical",
    "causal",
    "quasi-experimental",
    "replication"
  ]
};

const sampleText = `NSF EDU Core Research 21-588, National Science Foundation, 2026-10-01, Best flagship match for Digital Promise style research on STEM learning environments broadening participation STEM workforce development AI-enabled education data and learning sciences. Award ceiling 2500000. Link http://www.nsf.gov/publications/pub_summ.jsp?ods_key=nsf21588
NSF TechAccess AI-Ready America 26-508, National Science Foundation, 2026-07-16, Strong match for AI literacy public-serving organizations workforce upskilling partnerships and practical implementation at national scale. Award ceiling 4000000. Link http://www.nsf.gov/publications/pub_summ.jsp?ods_key=nsf26508
NSF Integrated Data Systems and Services 26-509, National Science Foundation, 2026-07-28, Strong infrastructure match for open data-intensive and AI-driven science education cyberinfrastructure integrated data systems and services. Award ceiling 30000000. Link http://www.nsf.gov/publications/pub_summ.jsp?ods_key=nsf26509
NSF Science of Learning and Augmented Intelligence PD-19-127Y, National Science Foundation, 2026-08-05, Excellent fit for human-centered AI learning sciences cognitive social cultural and technology-augmented learning research. Link http://www.nsf.gov/funding/pgm_summ.jsp?pims_id=505731
NSF Improving Undergraduate STEM Education 23-510, National Science Foundation, 2026-07-15, Fit for evidence-based STEM learning innovation evaluation and AI or data-enabled undergraduate learning improvement. Award ceiling 2000000. Link http://www.nsf.gov/publications/pub_summ.jsp?ods_key=nsf23510
NSF Research Experiences for Teachers in Engineering and Computer Science 24-503, National Science Foundation, 2026-10-14, Strong partnership match for K-14 educator research experiences translating computer science AI and engineering research into classroom activities. Link http://www.nsf.gov/publications/pub_summ.jsp?ods_key=nsf24503
NSF Robert Noyce Teacher Scholarship Program 23-586, National Science Foundation, 2026-08-25, Teacher workforce and high-need district match for recruiting preparing retaining K-12 STEM teachers and teacher leaders. Award ceiling 3250000. Link http://www.nsf.gov/publications/pub_summ.jsp?ods_key=nsf23586
Teacher Quality Partnership FY26 DOL-OESE-34066, Department of Education, 2026-06-23, Urgent teacher preparation opportunity for evidence-backed professional development teacher quality recruitment and partnership with IHEs districts and nonprofits. Estimated funding 70000000. Link https://www.ed.gov/grants-and-programs/teacher-preparation-grants/teacher-quality-partnership-program
Competitive Grants for State Assessments DOL-OESE-34017, Department of Education, 2026-06-16, Urgent assessment innovation fit covering meaningful learning opportunities improved scoring score reporting student growth and comprehensive academic assessment systems. Award ceiling 4000000. Link https://www.ed.gov/grants-and-programs/grants-birth-grade-12/school-and-community-improvement-grants/competitive-grants-state-assessments
National Comprehensive Center on Improving Literacy for Students with Disabilities 84.283D, Department of Education, 2026-06-30, Literacy disabilities and technical assistance fit aligned with accessible evidence-based instruction capacity building and learner variability. Award ceiling 1500000. Link https://www.ed.gov/grants-and-programs/grants-birth-grade-12/school-and-community-improvement-grants/comprehensive-centers-program-national-comprehensive-center-improving-literacy-students
Accessible Education Video Projects 84.327C, Department of Education, 2026-06-26, Accessibility technology media and materials opportunity for classroom educational videos captioning video description and students with disabilities. Award ceiling 1050000.
National Center for Accessible Education Videos 84.327N, Department of Education, 2026-06-26, National center opportunity for accessible educational media technology and timely materials for students with disabilities. Estimated funding 2600000.
OSERS OSEP National Assessment Center 84.326G, Department of Education, 2026-07-20, Assessment technical assistance fit for improving participation and performance of children with disabilities on state and districtwide assessments. Award ceiling 1000000.
National Professional Development Program DOL-OESE-34120, Department of Education, 2026-07-14, Professional learning fit for pre-service and in-service educator development in consortia with SEAs and LEAs. Award ceiling 1000000. Link https://www.ed.gov/grants-and-programs/teacher-preparation-grants/national-professional-development-program
Postsecondary Student Success Grant 84.116M, Department of Education, 2026-06-29, Data and rigorous evaluation fit for retention transfer credit accumulation completion and scaling evidence-based student success strategies. Award ceiling 8000000
Special Education Teacher Apprenticeships 84.325J, Department of Education, 2026-07-13, Workforce readiness and special education personnel pathway fit focused on research-based preparation and registered apprenticeships. Award ceiling 1000000.`;

const state = {
  opportunities: [],
  filtered: [],
  minFit: 0,
  source: "Weekly scan",
  scannedAt: ""
};

const els = {
  bulkInput: document.querySelector("#bulkInput"),
  scanButton: document.querySelector("#scanButton"),
  loadSampleButton: document.querySelector("#loadSampleButton"),
  profileSelect: document.querySelector("#profileSelect"),
  sourceSelect: document.querySelector("#sourceSelect"),
  hidePastDeadlines: document.querySelector("#hidePastDeadlines"),
  hideNoDeadlines: document.querySelector("#hideNoDeadlines"),
  resultsList: document.querySelector("#resultsList"),
  exportButton: document.querySelector("#exportButton"),
  totalCount: document.querySelector("#totalCount"),
  hotCount: document.querySelector("#hotCount"),
  withDeadlineCount: document.querySelector("#withDeadlineCount"),
  withoutDeadlineCount: document.querySelector("#withoutDeadlineCount"),
  deadlineCount: document.querySelector("#deadlineCount"),
  viewTitle: document.querySelector("#viewTitle"),
  scanMeta: document.querySelector("#scanMeta"),
  viewMeta: document.querySelector("#viewMeta")
};

function parseInput(text) {
  return text
    .split(/\n+/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line, index) => {
      const cols = splitCsvLine(line);
      if (cols.length >= 4) {
        return {
          id: `${Date.now()}-${index}`,
          title: cols[0],
          source: cols[1],
          deadline: normalizeDeadline(cols[2]),
          description: cols.slice(3).join(", "),
          url: extractUrl(cols.slice(3).join(", "))
        };
      }

      const dateMatch = line.match(/\b(20\d{2}[-/]\d{1,2}[-/]\d{1,2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+20\d{2})\b/i);
      const deadline = dateMatch ? normalizeDeadline(dateMatch[0]) : "";
      const cleanLine = deadline ? line.replace(dateMatch[0], "").replace(/\s{2,}/g, " ").trim() : line;
      const title = cleanLine.length > 90 ? `${cleanLine.slice(0, 87)}...` : cleanLine;

      return {
        id: `${Date.now()}-${index}`,
        title,
        source: "Pasted lead",
        deadline,
        description: line,
        url: extractUrl(line)
      };
    });
}

function normalizeLoadedOpportunity(item, index) {
  return {
    id: item.id || `loaded-${index}`,
    title: item.title || "Untitled opportunity",
    source: item.source || item.agency || "Unknown source",
    sourceType: item.sourceType || "",
    deadline: normalizeDeadline(item.deadline || item.closeDate || ""),
    description: item.description || item.summary || "",
    url: item.url || "",
    number: item.number || "",
    posted: normalizeDeadline(item.posted || item.postedDate || ""),
    awardCeiling: item.awardCeiling || "",
    estimatedFunding: item.estimatedFunding || "",
    indirectRate: item.indirectRate || item.indirectCostRate || "",
    eligibility: Array.isArray(item.eligibility) ? item.eligibility : [],
    fit: item.fit,
    matchedTerms: Array.isArray(item.matchedTerms) ? item.matchedTerms : []
  };
}

function splitCsvLine(line) {
  const values = [];
  let current = "";
  let quoted = false;

  for (let i = 0; i < line.length; i += 1) {
    const char = line[i];
    if (char === '"') {
      quoted = !quoted;
    } else if (char === "," && !quoted) {
      values.push(current.trim());
      current = "";
    } else {
      current += char;
    }
  }

  values.push(current.trim());
  return values;
}

function normalizeDeadline(value) {
  if (!value) return "";
  const parsed = new Date(value.replace(/\//g, "-"));
  if (Number.isNaN(parsed.getTime())) return value;
  return parsed.toISOString().slice(0, 10);
}

function extractUrl(value) {
  const match = String(value || "").match(/https?:\/\/[^\s)]+/);
  return match ? match[0] : "";
}

function getProfileTerms() {
  return profiles[els.profileSelect.value] || [];
}

function getSelectedTopicLabel() {
  return els.profileSelect.options[els.profileSelect.selectedIndex]?.textContent || "selected topic";
}

function getSelectedSourceLabel() {
  return els.sourceSelect?.options[els.sourceSelect.selectedIndex]?.textContent || "all agencies / sources";
}

function getTopicMatch(opportunity) {
  if (els.profileSelect.value === "all") return ["all"];
  const profileTerms = getProfileTerms();
  const haystack = `${opportunity.title} ${opportunity.source} ${opportunity.description}`.toLowerCase();
  return profileTerms.filter((term) => termMatches(haystack, term));
}

function scoreOpportunity(opportunity) {
  const topicMatched = getTopicMatch(opportunity);
  const matched = els.profileSelect.value === "all" ? opportunity.matchedTerms || [] : topicMatched;
  const haystack = `${opportunity.title} ${opportunity.source} ${opportunity.description} ${(opportunity.eligibility || []).join(" ")}`.toLowerCase();
  const sourceBoost = /(nsf|ies|education|school|district|foundation|agency|philanthropy)/i.test(opportunity.source) ? 10 : 0;
  const methodBoost = /(evaluation|randomized|mixed-method|longitudinal|evidence|validity|implementation|pilot)/i.test(haystack) ? 12 : 0;
  const urgencyBoost = daysUntil(opportunity.deadline) <= 30 && daysUntil(opportunity.deadline) >= 0 ? 6 : 0;
  const fit = Math.min(100, Math.round(28 + matched.length * 8 + sourceBoost + methodBoost + urgencyBoost));
  const reasonTerms = [...new Set([...(opportunity.matchedTerms || []), ...matched])];

  return {
    ...opportunity,
    fit,
    topicMatched,
    matched: reasonTerms.slice(0, 7),
    days: daysUntil(opportunity.deadline)
  };
}

function termMatches(haystack, term) {
  const escaped = term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const shortOrAcronym = term.length <= 4 || term === term.toUpperCase();
  const pattern = shortOrAcronym ? `\\b${escaped}\\b` : `(^|[^a-z0-9])${escaped}([^a-z0-9]|$)`;
  return new RegExp(pattern, "i").test(haystack);
}

function daysUntil(deadline) {
  if (!deadline) return Number.POSITIVE_INFINITY;
  const date = new Date(`${deadline}T23:59:59`);
  if (Number.isNaN(date.getTime())) return Number.POSITIVE_INFINITY;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return Math.ceil((date - today) / 86400000);
}

function applyFilters() {
  const topicItems = state.opportunities
    .map(scoreOpportunity)
    .filter((item) => item.topicMatched.length > 0)
    .filter((item) => item.fit >= state.minFit)
    .filter(passesDeadlineFilters);
  populateSourceFilter(topicItems);
  const selectedSource = els.sourceSelect?.value || "all";

  state.filtered = topicItems
    .filter((item) => selectedSource === "all" || formatSource(item) === selectedSource)
    .sort((a, b) => a.days - b.days || b.fit - a.fit);

  render(topicItems);
}

function passesDeadlineFilters(item) {
  if (els.hidePastDeadlines?.checked && item.deadline && item.days < 0) {
    return false;
  }
  if (els.hideNoDeadlines?.checked && !item.deadline) {
    return false;
  }
  return true;
}

function populateSourceFilter(items) {
  if (!els.sourceSelect) return;
  const currentValue = els.sourceSelect.value || "all";
  const sources = [...new Set(items.map(formatSource).filter(Boolean))].sort((a, b) => a.localeCompare(b));
  const nextValue = currentValue === "all" || sources.includes(currentValue) ? currentValue : "all";
  els.sourceSelect.innerHTML = [
    `<option value="all">All agencies / sources</option>`,
    ...sources.map((source) => `<option value="${escapeHtml(source)}">${escapeHtml(source)}</option>`)
  ].join("");
  els.sourceSelect.value = nextValue;
}

function render(topicItems = state.filtered) {
  const withDeadlineCount = state.filtered.filter((item) => Boolean(item.deadline)).length;
  const withoutDeadlineCount = state.filtered.length - withDeadlineCount;
  els.totalCount.textContent = String(state.filtered.length);
  els.hotCount.textContent = String(state.filtered.filter((item) => item.fit >= 85).length);
  els.withDeadlineCount.textContent = String(withDeadlineCount);
  els.withoutDeadlineCount.textContent = String(withoutDeadlineCount);
  els.deadlineCount.textContent = String(state.filtered.filter((item) => item.days >= 0 && item.days <= 21).length);
  const sourceLabel = els.sourceSelect?.value === "all" ? "" : ` from ${getSelectedSourceLabel()}`;
  els.viewTitle.textContent = state.filtered.length
    ? els.profileSelect.value === "all"
      ? `${state.filtered.length} funding opportunities${sourceLabel}`
      : `${state.filtered.length} ${getSelectedTopicLabel()} opportunities${sourceLabel}`
    : state.opportunities.length
      ? els.profileSelect.value === "all"
        ? "No opportunities under the current filters"
        : `No ${getSelectedTopicLabel()} matches`
      : "No opportunities scanned yet";
  const scanLabel = state.scannedAt ? `Last scanned ${formatDateTime(state.scannedAt)}` : "Using local fallback data";
  els.scanMeta.textContent = `${scanLabel}. Source: ${state.source}.`;
  els.viewMeta.textContent = `${scanLabel}. ${withDeadlineCount} with deadline, ${withoutDeadlineCount} without deadline in this view. ${topicItems.length} matching opportunities before agency/source selection.`;

  if (!state.filtered.length) {
    els.resultsList.innerHTML = `
      <div class="empty-state">
        <h2>${state.opportunities.length ? "Try lowering the fit threshold or search terms." : "Paste leads or load the sample set to begin."}</h2>
        <p>The scanner extracts basic fields, scores topical fit, flags urgency, and keeps a shortlist ready for CSV export.</p>
      </div>
    `;
    return;
  }

  const federalItems = state.filtered.filter((item) => !item.sourceType || item.sourceType === "Federal/other" || item.sourceType === "Federal education research");
  const foundationItems = state.filtered.filter((item) => item.sourceType === "Private foundation");
  const stateItems = state.filtered.filter((item) => item.sourceType === "State funding");
  const otherItems = state.filtered.filter(
    (item) => item.sourceType && !["Federal/other", "Federal education research", "Private foundation", "State funding"].includes(item.sourceType)
  );
  els.resultsList.innerHTML = [
    renderResultSection("Grants.gov and Federal Opportunities", federalItems, "primary"),
    renderResultSection("Private Foundation Opportunities", foundationItems, "foundation"),
    renderResultSection("State Funding Opportunities", stateItems, "state"),
    renderResultSection("Other Watchlist Sources", otherItems, "other")
  ].join("");
}

function renderResultSection(title, items, variant = "") {
  const subtitle = items.length === 1 ? "1 opportunity" : `${items.length} opportunities`;
  return `
    <div class="result-section ${variant ? `section-${variant}` : ""}">
      <div class="section-heading">
        <div>
          <p class="section-kicker">${escapeHtml(getSectionKicker(variant))}</p>
          <h3>${escapeHtml(title)}</h3>
        </div>
        <span>${escapeHtml(subtitle)}</span>
      </div>
      ${
        items.length
          ? items.map(renderRow).join("")
          : `<div class="section-empty">No matching opportunities in this section.</div>`
      }
    </div>
  `;
}

function getSectionKicker(variant) {
  if (variant === "primary") return "Primary source";
  if (variant === "foundation") return "Private funders";
  if (variant === "state") return "State agencies";
  return "Additional sources";
}

function renderRow(item) {
  const deadlineClass = item.days < 0 ? "past" : item.days <= 21 ? "urgent" : "";
  const deadlineLabel = item.deadline
    ? `${item.deadline}${Number.isFinite(item.days) ? ` (${formatDays(item.days)})` : ""}`
    : "Not listed";
  const reasons = item.matched.length ? item.matched : ["education relevance"];

  return `
    <article class="result-row">
      <div class="table-cell opportunity-cell" data-label="Opportunity">
        <p class="opportunity-title">${item.url ? `<a href="${escapeHtml(item.url)}" target="_blank" rel="noreferrer">${escapeHtml(item.title)}</a>` : escapeHtml(item.title)}</p>
        <p class="meta">${escapeHtml([item.number, `Fit ${item.fit}`].filter(Boolean).join(" | "))}</p>
        <div class="reasons">${reasons.map((reason) => `<span class="reason">${escapeHtml(reason)}</span>`).join("")}</div>
      </div>
      <div class="table-cell source-cell" data-label="Agency / Source">${escapeHtml(formatSource(item))}</div>
      <div class="table-cell deadline ${deadlineClass}" data-label="Deadline">${escapeHtml(deadlineLabel)}</div>
      <div class="table-cell" data-label="Posted Date">${escapeHtml(item.posted || "Not listed")}</div>
      <div class="table-cell" data-label="Award Ceiling / Estimated Funding">${escapeHtml(formatAward(item))}</div>
      <div class="table-cell" data-label="Eligibility Categories">${escapeHtml(summarizeEligibility(item))}</div>
      <div class="table-cell description-cell" data-label="Description">
        ${escapeHtml(formatDescription(item.description))}
      </div>
    </article>
  `;
}

function formatSource(item) {
  return [item.source, item.sourceType].filter(Boolean).join(" | ") || "Unknown source";
}

function summarizeEligibility(item) {
  const tags = inferOpportunityTags(item);
  const applicantTypes = (item.eligibility || [])
    .map(cleanEligibilityLabel)
    .filter(Boolean)
    .slice(0, 2);
  const summary = [...tags, ...applicantTypes].filter(Boolean);
  return summary.length ? summary.join("; ") : "Check NOFO";
}

function inferOpportunityTags(item) {
  const haystack = `${item.title} ${item.source} ${item.description} ${(item.eligibility || []).join(" ")}`.toLowerCase();
  const tags = [];
  if (/(nonprofit|non-profit|non profit|research|university|institution of higher education|\bihe\b)/i.test(haystack)) {
    tags.push("Nonprofit/research");
  }
  if (/(postsecondary|higher education|undergraduate|community college|\bihe\b|college|career|workforce|adult education|credential|pathway)/i.test(haystack)) {
    tags.push("Postsecondary/workforce");
  }
  if (/(literacy|reading|writing|english language arts|\bela\b|english learner|language arts)/i.test(haystack)) {
    tags.push("ELA/literacy");
  }
  if (/(state educational agency|\bsea\b|local educational agency|\blea\b|district|school|k-12|secondary school)/i.test(haystack)) {
    tags.push("K-12/agency");
  }
  return [...new Set(tags)].slice(0, 3);
}

function cleanEligibilityLabel(value) {
  return String(value || "")
    .replace(/\s*\(see text field entitled "Additional Information on Eligibility" for clarification\)/i, "")
    .replace(/Others/i, "Other eligible applicants")
    .trim();
}

function formatAward(item) {
  const ceiling = formatMoney(item.awardCeiling);
  const estimated = formatMoney(item.estimatedFunding);
  if (ceiling && estimated) return `${ceiling} ceiling; ${estimated} total`;
  if (ceiling) return `${ceiling} ceiling`;
  if (estimated) return `${estimated} total`;
  return "Not listed";
}

function formatMoney(value) {
  const number = Number(String(value || "").replace(/[$,]/g, ""));
  if (!Number.isFinite(number) || number <= 0) return "";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0
  }).format(number);
}

function formatIndirectRate(item) {
  return item.indirectRate || "Check NOFO";
}

function formatDescription(value) {
  const text = String(value || "").replace(/\s+/g, " ").trim();
  if (!text) return "Not listed";
  return text.length > 360 ? `${text.slice(0, 357)}...` : text;
}

function formatDateTime(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
    timeZoneName: "short"
  }).format(date);
}

function formatDays(days) {
  if (days < 0) return "past";
  if (days === 0) return "today";
  if (days === 1) return "1 day";
  return `${days} days`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function exportCsv() {
  if (!state.filtered.length) return;
  const header = [
    "title",
    "source",
    "source_type",
    "deadline",
    "posted",
    "award_amount",
    "indirect_rate",
    "eligibility",
    "fit",
    "matched_terms",
    "description"
  ];
  const rows = state.filtered.map((item) => [
    item.title,
    item.source,
    item.sourceType || "",
    item.deadline,
    item.posted || "",
    formatAward(item),
    formatIndirectRate(item),
    summarizeEligibility(item),
    item.fit,
    item.matched.join("; "),
    item.description
  ]);
  const csv = [header, ...rows]
    .map((row) => row.map((value) => `"${String(value).replaceAll('"', '""')}"`).join(","))
    .join("\n");
  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "education-research-opportunities.csv";
  link.click();
  URL.revokeObjectURL(url);
}

els.scanButton?.addEventListener("click", () => {
  state.opportunities = parseInput(els.bulkInput.value);
  state.source = "Custom pasted leads";
  state.scannedAt = "";
  applyFilters();
});

els.loadSampleButton?.addEventListener("click", () => {
  loadWeeklyScan();
});

els.profileSelect?.addEventListener("change", applyFilters);
els.sourceSelect?.addEventListener("change", applyFilters);
els.hidePastDeadlines?.addEventListener("change", applyFilters);
els.hideNoDeadlines?.addEventListener("change", applyFilters);
els.exportButton?.addEventListener("click", exportCsv);

document.querySelectorAll("[data-min-fit]").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll("[data-min-fit]").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    state.minFit = Number(button.dataset.minFit);
    applyFilters();
  });
});

async function loadWeeklyScan() {
  try {
    const response = await fetch("data/opportunities.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`Data request failed with ${response.status}`);
    const data = await response.json();
    state.opportunities = (data.opportunities || []).map(normalizeLoadedOpportunity);
    state.source = data.source || "Weekly scan";
    state.scannedAt = data.scannedAt || "";
    els.bulkInput.value = "";
    applyFilters();
  } catch (error) {
    state.opportunities = parseInput(sampleText);
    state.source = "Local fallback data";
    state.scannedAt = "";
    els.bulkInput.value = "";
    applyFilters();
  }
}

loadWeeklyScan();
