#!/usr/bin/env python3
"""
Build a `short_description` column: one plain sentence saying what each
resource actually is.

The rightmost table column used to show `dataset_artifact_evidence`, which
holds provenance notes ("Hugging Face dataset repository URL plus retained
dataset inventory row") rather than anything a reader could use. The real prose
lives in `original_information`, buried under scraper boilerplate like
"Evidence: Hugging Face dataset: # <Title> ## Dataset Description ...".

This does the cleaning once, in Python, so it is auditable and re-runnable -
rather than doing regex work in the browser on every page load.

Source preference, best first:
  1. description            - hand-written, already clean
  2. original_information   - real prose, needs boilerplate stripped
  3. educational_use_case   - what it's for, if not what it is
  4. notes                  - last resort
  5. a generated summary from type/subject/source, so nothing is blank

Run:  python3 generate-descriptions.py
"""

import re
import sys

import pandas as pd

CSV = 'data/k12_inventory_latest.csv'
MAX_LEN = 240

# Scraper prefixes that carry no meaning for a reader.
_PREFIXES = [
    r'^Evidence\s*:\s*',
    r'^(Hugging\s*Face|HuggingFace|GitHub|ArXiv|OpenReview|Papers\s*with\s*Code)'
    r'[^:]{0,40}:\s*',
    r'^(Dataset|Model|Benchmark)\s+(Card|Repository)\s*:\s*',
]

# Section headings the scrapers drag along.
_HEADINGS = [
    r'Dataset\s+(Summary|Description|Details|Overview|Structure)',
    r'Model\s+(Card|Description|Details)',
    r'Table\s+of\s+Contents',
    r'(Description|Overview|Summary)\s*:',
]


def clean_prose(raw, name):
    """Strip scraper boilerplate, markdown, and a leading echo of the title."""
    if not isinstance(raw, str) or not raw.strip():
        return ''
    t = raw.strip()

    for p in _PREFIXES:
        t = re.sub(p, '', t, flags=re.I)

    # Markdown noise
    t = re.sub(r'#+', ' ', t)
    t = re.sub(r'\*\*|__|`|~~', '', t)
    t = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', t)   # links -> label
    t = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', t)       # images
    t = re.sub(r'\s+', ' ', t).strip()

    # Drop a leading repetition of the resource name. Match the FULL name -
    # truncating it (e.g. to 60 chars) can slice a word in half and leave
    # fragments like "aset A comprehensive dataset of...".
    if isinstance(name, str) and name.strip():
        t = re.sub(r'^\s*' + re.escape(name.strip()) + r'\s*', '', t, flags=re.I)

    for h in _HEADINGS:
        t = re.sub(r'^\s*' + h + r'\s*', '', t, flags=re.I)
        t = re.sub(r'\s+' + h + r'\s+', '. ', t, flags=re.I)

    t = re.sub(r'\s+', ' ', t).strip(' -:;,.')
    return t


def truncate(t, limit=MAX_LEN):
    """Cut at a sentence boundary when possible, else at a word boundary."""
    if len(t) <= limit:
        return t
    window = t[:limit]
    for end in ('. ', '; '):
        i = window.rfind(end)
        if i > limit * 0.5:
            return window[:i + 1].strip()
    i = window.rfind(' ')
    return (window[:i] if i > 0 else window).strip(' -:;,.') + '...'


def generated_summary(row):
    """Last-resort one-liner assembled from the structured fields, so the
    column is never blank."""
    kind = str(row.get('resource_subtype') or 'Resource').replace('_', ' ')
    subject = str(row.get('subject_canonical') or '').strip()
    source = str(row.get('discovery_source') or row.get('author_name') or '').strip()
    grade = str(row.get('grade_span_group') or '').strip()

    s = f'{kind}'
    if subject and subject.lower() not in ('nan', 'cross-subject / general'):
        s += f' covering {subject}'
    if grade and grade.lower() != 'nan':
        s += f' for {grade}'
    if source and source.lower() not in ('nan', 'curated'):
        s += f', via {source}'
    return s + '.'


def build(row):
    v = row.get('description')
    if isinstance(v, str) and v.strip():
        return truncate(re.sub(r'\s+', ' ', v.strip())), 'description'

    c = clean_prose(row.get('original_information'), row.get('resource_name'))
    if len(c) >= 40:
        return truncate(c), 'original_information'

    for f in ('educational_use_case', 'notes'):
        v = row.get(f)
        # Require real substance. Many `notes` values just echo the resource
        # name ("KORA Apps Methodology") or are a single word ("Benchmarking"),
        # which reads as a description but tells the reader nothing.
        if isinstance(v, str) and len(v.strip()) >= 25:
            name = str(row.get('resource_name') or '').strip().lower()
            if v.strip().lower() != name:
                return truncate(re.sub(r'\s+', ' ', v.strip())), f

    if len(c) > 0:
        return truncate(c), 'original_information'

    return generated_summary(row), 'generated'


def main():
    df = pd.read_csv(CSV)

    built = [build(r) for _, r in df.iterrows()]
    df['short_description'] = [b[0] for b in built]
    sources = pd.Series([b[1] for b in built])

    blank = (df['short_description'].astype(str).str.strip() == '').sum()
    if blank:
        sys.exit(f'ERROR: {blank} rows still have no description')

    # Keep column order stable.
    cols = list(df.columns)
    cols.remove('short_description')
    cols.insert(cols.index('resource_name') + 1, 'short_description')
    df[cols].to_csv(CSV, index=False)

    print(f'Wrote short_description for all {len(df)} rows.\n')
    print('Source used:')
    for k, v in sources.value_counts().items():
        print(f'  {k:22} {v:3}')
    lens = df['short_description'].str.len()
    print(f'\nLength: min {lens.min()}, median {int(lens.median())}, max {lens.max()}')

    # Fragment check: a description starting lowercase mid-word usually means
    # the title-strip cut incorrectly.
    suspect = df[df['short_description'].str.match(r'^[a-z]{1,3}\s')]
    print(f'\nPossible fragments: {len(suspect)}')
    for _, r in suspect.head(5).iterrows():
        print(f"  ! {str(r['resource_name'])[:40]} -> {r['short_description'][:60]}")


if __name__ == '__main__':
    main()
