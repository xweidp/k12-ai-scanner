// K-12 AI Resource Scanner app
// Loads and filters datasets, benchmarks, and models for K-12 education

const state = {
  resources: [],
  filtered: [],
  minFit: 0,
  source: "Weekly scan",
  scannedAt: ""
};

const els = {
  bulkInput: document.querySelector("#bulkInput"),
  searchButton: document.querySelector("#searchButton"),
  reloadButton: document.querySelector("#reloadButton"),
  resourceTypeSelect: document.querySelector("#resourceTypeSelect"),
  subjectSelect: document.querySelector("#subjectSelect"),
  gradeBandSelect: document.querySelector("#gradeBandSelect"),
  sourceSelect: document.querySelector("#sourceSelect"),
  licenseToggle: document.querySelector("#licenseToggle"),
  modalityToggle: document.querySelector("#modalityToggle"),
  resultsList: document.querySelector("#resultsList"),
  exportButton: document.querySelector("#exportButton"),
  totalCount: document.querySelector("#totalCount"),
  highFitCount: document.querySelector("#highFitCount"),
  datasetCount: document.querySelector("#datasetCount"),
  benchmarkCount: document.querySelector("#benchmarkCount"),
  modelCount: document.querySelector("#modelCount"),
  viewTitle: document.querySelector("#viewTitle"),
  scanMeta: document.querySelector("#scanMeta"),
  viewMeta: document.querySelector("#viewMeta")
};

// -------------------------------------------------------------------------
// Custom search: parse pasted titles/urls and search loaded resources
// -------------------------------------------------------------------------

function searchResources(query) {
  if (!query.trim()) {
    applyFilters();
    return;
  }

  const terms = query
    .split(/\n+/)
    .map((line) => line.trim().toLowerCase())
    .filter(Boolean);

  const matches = state.resources.filter((res) => {
    const haystack = `${res.title} ${res.source} ${res.description}`.toLowerCase();
    return terms.some((term) => haystack.includes(term));
  });

  state.filtered = matches.sort((a, b) => b.fit - a.fit || a.title.localeCompare(b.title));
  render();
}

// -------------------------------------------------------------------------
// Filtering
// -------------------------------------------------------------------------

function getSelectedResourceType() {
  return els.resourceTypeSelect?.value || "all";
}

function getSelectedSubject() {
  return els.subjectSelect?.value || "all";
}

function getSelectedGradeBand() {
  return els.gradeBandSelect?.value || "all";
}

function getSelectedSource() {
  return els.sourceSelect?.value || "all";
}

function getSelectedSourceLabel() {
  return els.sourceSelect?.options[els.sourceSelect.selectedIndex]?.textContent || "all sources";
}

function passesFilters(res) {
  const resourceType = getSelectedResourceType();
  const subject = getSelectedSubject();
  const gradeBand = getSelectedGradeBand();
  const source = getSelectedSource();
  const licenseOpen = els.licenseToggle?.checked;
  const hasModality = els.modalityToggle?.checked;

  if (resourceType !== "all" && res.resourceType !== resourceType) return false;
  if (subject !== "all" && !(res.subjects || []).includes(subject)) return false;
  if (gradeBand !== "all" && res.gradeBand !== gradeBand) return false;
  if (source !== "all" && res.source !== source) return false;
  if (licenseOpen && /^see |^custom|^unknown/i.test(res.license || "")) return false;
  if (hasModality && (!res.modality || res.modality.length === 0)) return false;

  return res.fit >= state.minFit;
}

function applyFilters() {
  const all = state.resources
    .filter(passesFilters)
    .sort((a, b) => b.fit - a.fit || a.title.localeCompare(b.title));

  populateFilterDropdowns(all);
  state.filtered = all;
  render();
}

function populateFilterDropdowns(items) {
  // Subjects
  if (els.subjectSelect) {
    const subjects = [...new Set(items.flatMap((r) => r.subjects || []))].sort();
    const currentSubject = els.subjectSelect.value || "all";
    els.subjectSelect.innerHTML = [
      `<option value="all">All subjects</option>`,
      ...subjects.map((s) => `<option value="${escapeHtml(s)}">${escapeHtml(s)}</option>`)
    ].join("");
    els.subjectSelect.value = subjects.includes(currentSubject) ? currentSubject : "all";
  }

  // Sources
  if (els.sourceSelect) {
    const sources = [...new Set(items.map((r) => r.source))].filter(Boolean).sort();
    const currentSource = els.sourceSelect.value || "all";
    els.sourceSelect.innerHTML = [
      `<option value="all">All sources</option>`,
      ...sources.map((s) => `<option value="${escapeHtml(s)}">${escapeHtml(s)}</option>`)
    ].join("");
    els.sourceSelect.value = sources.includes(currentSource) ? currentSource : "all";
  }
}

// -------------------------------------------------------------------------
// Rendering
// -------------------------------------------------------------------------

function render() {
  const total = state.filtered.length;
  const highFit = state.filtered.filter((r) => r.fit >= 85).length;
  const datasets = state.filtered.filter((r) => r.resourceType === "Dataset").length;
  const benchmarks = state.filtered.filter((r) => r.resourceType === "Benchmark").length;
  const models = state.filtered.filter((r) => r.resourceType === "Model").length;

  els.totalCount.textContent = String(total);
  els.highFitCount.textContent = String(highFit);
  els.datasetCount.textContent = String(datasets);
  els.benchmarkCount.textContent = String(benchmarks);
  els.modelCount.textContent = String(models);

  const resourceTypeLabel = getSelectedResourceType() === "all" ? "" : ` ${getSelectedResourceType()}`;
  const sourceLabel = getSelectedSource() === "all" ? "" : ` from ${getSelectedSourceLabel()}`;

  els.viewTitle.textContent = total
    ? `${total}${resourceTypeLabel} K-12 resources${sourceLabel}`
    : state.resources.length
      ? "No resources match current filters"
      : "No resources loaded yet";

  const scanLabel = state.scannedAt ? `Last scanned ${formatDateTime(state.scannedAt)}` : "Using fallback data";
  els.scanMeta.textContent = `${scanLabel}. Source: ${state.source}.`;
  els.viewMeta.textContent = `${scanLabel}. ${total} resources in current view.`;

  if (!total) {
    els.resultsList.innerHTML = `
      <div class="empty-state">
        <h2>${state.resources.length ? "Try adjusting filters or search terms." : "Paste search terms or load the weekly scan."}</h2>
        <p>The scanner curates K-12 AI datasets, benchmarks, and models from education-focused catalogs and research hubs.</p>
      </div>
    `;
    return;
  }

  // Group by resource type
  const groups = [
    { type: "Dataset", items: state.filtered.filter((r) => r.resourceType === "Dataset") },
    { type: "Benchmark", items: state.filtered.filter((r) => r.resourceType === "Benchmark") },
    { type: "Model", items: state.filtered.filter((r) => r.resourceType === "Model") },
    { type: "Competition", items: state.filtered.filter((r) => r.resourceType === "Competition") }
  ].filter((g) => g.items.length > 0);

  els.resultsList.innerHTML = groups.map((group) => renderGroup(group.type, group.items)).join("");
}

function renderGroup(type, items) {
  const subtitle = items.length === 1 ? "1 resource" : `${items.length} resources`;
  return `
    <div class="result-section">
      <div class="section-heading">
        <div>
          <p class="section-kicker">${escapeHtml(type)}</p>
          <h3>${escapeHtml(type)}</h3>
        </div>
        <span>${escapeHtml(subtitle)}</span>
      </div>
      ${items.map(renderRow).join("")}
    </div>
  `;
}

function renderRow(res) {
  const subjects = (res.subjects || []).slice(0, 3).join(", ") || "Not tagged";
  const modality = (res.modality || []).join(", ") || "Not listed";

  return `
    <article class="result-row">
      <div class="table-cell resource-cell" data-label="Resource">
        <p class="resource-title">${res.url ? `<a href="${escapeHtml(res.url)}" target="_blank" rel="noreferrer">${escapeHtml(res.title)}</a>` : escapeHtml(res.title)}</p>
        <p class="meta">Fit ${res.fit}</p>
      </div>
      <div class="table-cell" data-label="Type">${escapeHtml(res.resourceType)}</div>
      <div class="table-cell" data-label="Source">${escapeHtml(res.source)}</div>
      <div class="table-cell" data-label="Subjects">${escapeHtml(subjects)}</div>
      <div class="table-cell" data-label="Grade Band">${escapeHtml(res.gradeBand)}</div>
      <div class="table-cell" data-label="Modality">${escapeHtml(modality)}</div>
      <div class="table-cell" data-label="License">${escapeHtml(res.license || "Not specified")}</div>
      <div class="table-cell description-cell" data-label="Description">${escapeHtml(formatDescription(res.description))}</div>
    </article>
  `;
}

function formatDescription(value) {
  const text = String(value || "").replace(/\s+/g, " ").trim();
  if (!text) return "No description";
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

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

// -------------------------------------------------------------------------
// CSV Export
// -------------------------------------------------------------------------

function exportCsv() {
  if (!state.filtered.length) return;
  const header = [
    "title",
    "resource_type",
    "source",
    "subjects",
    "grade_band",
    "modality",
    "license",
    "fit",
    "url",
    "description"
  ];
  const rows = state.filtered.map((res) => [
    res.title,
    res.resourceType,
    res.source,
    (res.subjects || []).join("; "),
    res.gradeBand,
    (res.modality || []).join("; "),
    res.license,
    res.fit,
    res.url,
    res.description
  ]);
  const csv = [header, ...rows]
    .map((row) => row.map((value) => `"${String(value).replaceAll('"', '""')}"`).join(","))
    .join("\n");
  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "k12-ai-resources.csv";
  link.click();
  URL.revokeObjectURL(url);
}

// -------------------------------------------------------------------------
// Data loading
// -------------------------------------------------------------------------

async function loadWeeklyScan() {
  try {
    const response = await fetch("data/resources.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`Data request failed with ${response.status}`);
    const data = await response.json();
    state.resources = data.resources || [];
    state.source = data.source || "Weekly scan";
    state.scannedAt = data.scannedAt || "";
    els.bulkInput.value = "";
    applyFilters();
  } catch (error) {
    console.warn("Failed to load resources.json:", error);
    state.resources = [];
    state.source = "No data available";
    state.scannedAt = "";
    els.bulkInput.value = "";
    applyFilters();
  }
}

// -------------------------------------------------------------------------
// Event listeners
// -------------------------------------------------------------------------

els.searchButton?.addEventListener("click", () => {
  searchResources(els.bulkInput.value);
});

els.reloadButton?.addEventListener("click", () => {
  loadWeeklyScan();
});

els.resourceTypeSelect?.addEventListener("change", applyFilters);
els.subjectSelect?.addEventListener("change", applyFilters);
els.gradeBandSelect?.addEventListener("change", applyFilters);
els.sourceSelect?.addEventListener("change", applyFilters);
els.licenseToggle?.addEventListener("change", applyFilters);
els.modalityToggle?.addEventListener("change", applyFilters);
els.exportButton?.addEventListener("click", exportCsv);

document.querySelectorAll("[data-min-fit]").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll("[data-min-fit]").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    state.minFit = Number(button.dataset.minFit);
    applyFilters();
  });
});

// -------------------------------------------------------------------------
// Initialization
// -------------------------------------------------------------------------

loadWeeklyScan();
