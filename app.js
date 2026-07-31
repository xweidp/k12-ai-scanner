// K-12 AI Inventory Browser
// Loads k12_inventory_latest.csv (v18 base + newly discovered resources)

const state = {
  resources: [],
  filtered: [],
  sortBy: null,
  sortAsc: true,
  scannedAt: new Date().toISOString()
};

const els = {
  resourceTypeSelect: document.querySelector("#resourceTypeSelect"),
  subjectSelect: document.querySelector("#subjectSelect"),
  gradeBandSelect: document.querySelector("#gradeBandSelect"),
  sourceSelect: document.querySelector("#sourceSelect"),
  verificationSelect: document.querySelector("#verificationSelect"),
  licenseToggle: document.querySelector("#licenseToggle"),
  resultsList: document.querySelector("#resultsList"),
  exportButton: document.querySelector("#exportButton"),
  totalCount: document.querySelector("#totalCount"),
  highFitCount: document.querySelector("#highFitCount"),
  datasetCount: document.querySelector("#datasetCount"),
  benchmarkCount: document.querySelector("#benchmarkCount"),
  modelCount: document.querySelector("#modelCount"),
  viewTitle: document.querySelector("#viewTitle"),
  scanMeta: document.querySelector("#scanMeta"),
  viewMeta: document.querySelector("#viewMeta"),
  reloadButton: document.querySelector("#reloadButton")
};

// Parse CSV line properly handling quoted fields
function parseCSVLine(line) {
  const result = [];
  let current = '';
  let inQuotes = false;

  for (let i = 0; i < line.length; i++) {
    const char = line[i];
    const nextChar = line[i + 1];

    if (char === '"') {
      if (inQuotes && nextChar === '"') {
        // Escaped quote
        current += '"';
        i++;
      } else {
        // Toggle quote state
        inQuotes = !inQuotes;
      }
    } else if (char === ',' && !inQuotes) {
      result.push(current.trim().replace(/^"(.*)"$/, '$1'));
      current = '';
    } else {
      current += char;
    }
  }
  result.push(current.trim().replace(/^"(.*)"$/, '$1'));
  return result;
}

// Load and parse CSV
function loadInventory() {
  fetch('data/k12_inventory_latest.csv')
    .then(r => {
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.text();
    })
    .then(csv => {
      const lines = csv.trim().split('\n');
      if (lines.length < 2) {
        showError('CSV file is empty');
        return;
      }

      const headers = parseCSVLine(lines[0]);
      console.log('CSV Headers:', headers);

      state.resources = lines.slice(1).map((line, idx) => {
        const values = parseCSVLine(line);
        const row = {};
        headers.forEach((h, i) => {
          row[h] = values[i] || '';
        });

        const resourceType = row.resource_subtype || 'Dataset';
        const subjectArea = row.subject_area || '';
        const source = row.discovery_source || row.author_name || 'Curated';

        return {
          id: row.record_id || `r-${idx}`,
          title: row.resource_name || 'Untitled',
          resourceType: resourceType,
          source: source,
          subjects: subjectArea
            .split(',')
            .map(s => s.trim())
            .filter(Boolean),
          gradeBand: row.grade_span_group || 'K-12',
          license: row.license_status_clean || 'Not listed',
          description: row.dataset_artifact_evidence || row.notes || '',
          url: row.url || '',
          publicationDate: row.publication_date || '',
          discoveryDate: row.discovery_date || '',
          readinessTier: row.final_readiness_index_tier || 'Not Reviewed',
          fit: parseInt(row.fit_score) || 50
        };
      });

      console.log(`Loaded ${state.resources.length} resources`);
      const withDates = state.resources.filter(r => r.publicationDate).length;
      console.log(`Resources with publication dates: ${withDates}`);
      if (state.resources[0]) {
        console.log(`Sample resource:`, state.resources[0]);
      }
      applyFilters();
      render();
    })
    .catch(err => {
      console.error('Load error:', err);
      showError(`Failed to load inventory: ${err.message}`);
    });
}

function showError(msg) {
  if (els.resultsList) {
    els.resultsList.innerHTML = `<div class="empty-state"><h2>Error: ${msg}</h2></div>`;
  }
}

function applyFilters() {
  const resourceType = els.resourceTypeSelect?.value || 'all';
  const subject = els.subjectSelect?.value || 'all';
  const gradeBand = els.gradeBandSelect?.value || 'all';
  const source = els.sourceSelect?.value || 'all';
  const verification = els.verificationSelect?.value || 'verified';
  const licenseOpen = els.licenseToggle?.checked;

  const isVerified = r => r.readinessTier && !r.readinessTier.includes('Not Reviewed');

  state.filtered = state.resources.filter(r => {
    if (resourceType !== 'all' && r.resourceType !== resourceType) return false;
    if (subject !== 'all' && !r.subjects.includes(subject)) return false;
    if (gradeBand !== 'all' && r.gradeBand !== gradeBand) return false;
    if (source !== 'all' && r.source !== source) return false;
    if (licenseOpen && /^not|^see|^custom|^unknown/i.test(r.license)) return false;

    // Verification filter
    if (verification === 'verified' && !isVerified(r)) return false;
    if (verification === 'new' && isVerified(r)) return false;

    return true;
  });

  applySorting();
  populateSelects();
  render();
}

function applySorting() {
  if (!state.sortBy) return;

  state.filtered.sort((a, b) => {
    let aVal = a[state.sortBy];
    let bVal = b[state.sortBy];

    // Handle dates
    if (state.sortBy === 'publicationDate' || state.sortBy === 'discoveryDate') {
      aVal = aVal ? new Date(aVal).getTime() : 0;
      bVal = bVal ? new Date(bVal).getTime() : 0;
    }

    // Handle strings
    if (typeof aVal === 'string') {
      aVal = aVal.toLowerCase();
      bVal = bVal.toLowerCase();
    }

    if (aVal < bVal) return state.sortAsc ? -1 : 1;
    if (aVal > bVal) return state.sortAsc ? 1 : -1;
    return 0;
  });
}

function populateSelects() {
  // Subjects
  const subjects = [...new Set(state.resources.flatMap(r => r.subjects))].sort();
  const subjectValue = els.subjectSelect?.value || 'all';
  if (els.subjectSelect) {
    els.subjectSelect.innerHTML = [
      '<option value="all">All subjects</option>',
      ...subjects.map(s => `<option value="${esc(s)}">${esc(s)}</option>`)
    ].join('');
    els.subjectSelect.value = subjectValue;
  }

  // Sources
  const sources = [...new Set(state.resources.map(r => r.source))].sort();
  const sourceValue = els.sourceSelect?.value || 'all';
  if (els.sourceSelect) {
    els.sourceSelect.innerHTML = [
      '<option value="all">All sources</option>',
      ...sources.map(s => `<option value="${esc(s)}">${esc(s)}</option>`)
    ].join('');
    els.sourceSelect.value = sourceValue;
  }
}

function render() {
  const counts = {
    total: state.filtered.length,
    high: state.filtered.filter(r => r.fit >= 70).length,
    dataset: state.filtered.filter(r => r.resourceType === 'Dataset').length,
    benchmark: state.filtered.filter(r => r.resourceType === 'Benchmark').length,
    model: state.filtered.filter(r => r.resourceType === 'Model').length
  };

  if (els.totalCount) els.totalCount.textContent = counts.total;
  if (els.highFitCount) els.highFitCount.textContent = counts.high;
  if (els.datasetCount) els.datasetCount.textContent = counts.dataset;
  if (els.benchmarkCount) els.benchmarkCount.textContent = counts.benchmark;
  if (els.modelCount) els.modelCount.textContent = counts.model;

  const verified = state.filtered.filter(r => !r.readinessTier?.includes('Not Reviewed')).length;
  const newCount = state.filtered.filter(r => r.readinessTier?.includes('Not Reviewed')).length;

  if (els.scanMeta) {
    els.scanMeta.textContent = `${verified} verified (high quality, manually reviewed). ${newCount} newly discovered (auto-found, need manual review).`;
  }

  if (els.viewTitle) {
    els.viewTitle.textContent = counts.total
      ? `${counts.total} K-12 resources`
      : state.resources.length > 0
        ? 'No resources match filters'
        : 'Loading...';
  }

  if (els.viewMeta) {
    els.viewMeta.textContent = `${counts.dataset} datasets, ${counts.benchmark} benchmarks, ${counts.model} models`;
  }

  if (!counts.total) {
    if (els.resultsList) {
      els.resultsList.innerHTML = `<div class="empty-state"><h2>${state.resources.length > 0 ? 'No resources match your filters.' : 'Loading inventory...'}</h2></div>`;
    }
    return;
  }

  if (els.resultsList) {
    els.resultsList.innerHTML = state.filtered.map(renderRow).join('');
  }
}

function renderRow(r) {
  const badge = r.readinessTier?.includes('Not Reviewed')
    ? '<span class="discovery-badge">NEW</span>'
    : '<span class="verified-badge">VERIFIED</span>';

  return `
    <article class="result-row">
      <div class="table-cell opportunity-cell">
        <p class="opportunity-title">
          ${r.url ? `<a href="${esc(r.url)}" target="_blank">${esc(r.title)}</a>` : esc(r.title)}
        </p>
        <p class="meta">${badge}</p>
      </div>
      <div class="table-cell">${esc(r.resourceType)}</div>
      <div class="table-cell">${r.subjects.join(', ') || 'General'}</div>
      <div class="table-cell">${esc(r.source)}</div>
      <div class="table-cell" style="font-weight: ${r.publicationDate ? 'bold' : 'normal'}">${r.publicationDate || '—'}</div>
      <div class="table-cell">${esc(r.license)}</div>
      <div class="table-cell description-cell">
        ${esc(r.description.slice(0, 80))}
      </div>
    </article>
  `;
}

function esc(s) {
  const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
  return String(s || '').replace(/[&<>"']/g, c => map[c]);
}

function exportCsv() {
  if (!state.filtered.length) return;
  const header = ['Title', 'Type', 'Source', 'License', 'Published', 'URL', 'Status'];
  const rows = state.filtered.map(r => [
    r.title, r.resourceType, r.source, r.license, r.publicationDate, r.url, r.readinessTier
  ]);
  const csv = [header, ...rows]
    .map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
    .join('\n');

  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `k12-inventory-${new Date().toISOString().split('T')[0]}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

// Event listeners
els.resourceTypeSelect?.addEventListener('change', applyFilters);
els.subjectSelect?.addEventListener('change', applyFilters);
els.gradeBandSelect?.addEventListener('change', applyFilters);
els.sourceSelect?.addEventListener('change', applyFilters);
els.verificationSelect?.addEventListener('change', applyFilters);
els.licenseToggle?.addEventListener('change', applyFilters);
els.exportButton?.addEventListener('click', exportCsv);
els.reloadButton?.addEventListener('click', loadInventory);

// Sort button click handler
document.querySelectorAll('.sort-btn').forEach(btn => {
  btn.addEventListener('click', (e) => {
    e.preventDefault();
    const sortField = btn.dataset.sort;
    if (state.sortBy === sortField) {
      state.sortAsc = !state.sortAsc;
    } else {
      state.sortBy = sortField;
      state.sortAsc = false; // Newest first by default
    }
    applyFilters();
  });
});

// Load on page load
loadInventory();
