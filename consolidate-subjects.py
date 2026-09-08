#!/usr/bin/env python3
"""
Collapse the free-text subject_area field into a small fixed taxonomy.

The raw subject_area values are hand-entered and semicolon-delimited, which left
49 distinct strings for 154 records - many of them one-offs like
"Cross-subject; Turkish language; audio". That makes the Subject dropdown
unusable. This writes a `subject_canonical` column with one of 9 buckets.

Rules are ordered: the first matching rule wins, so put the most specific first.
Language-learning resources land in "World Languages & Multilingual" even when
they also mention a content area, because that is the axis people filter on.
A resource that merely happens to be *in* another language (e.g. a Turkish math
dataset) keeps its content area.
"""

import re
import sys
import pandas as pd

CSV = 'data/k12_inventory_latest.csv'

# The 9 canonical buckets.
GENERAL = 'Cross-subject / General'
MATH = 'Mathematics'
SCIENCE = 'Science & STEM'
ELA = 'English Language Arts & Literacy'
WORLD_LANG = 'World Languages & Multilingual'
SOCIAL = 'Social Studies & Civics'
CS_AI = 'Computer Science & AI'
CAREER = 'Career & Financial Literacy'
POLICY = 'Education Policy & Special Education'

CANONICAL_ORDER = [
    GENERAL, MATH, SCIENCE, ELA, WORLD_LANG,
    SOCIAL, CS_AI, CAREER, POLICY,
]

# Major content areas, used to detect comprehensive state-standards dumps.
_BREADTH_MARKERS = [
    r'english language arts|\bela\b', r'\bmath', r'science',
    r'social studies|history', r'health education', r'physical education',
    r'fine arts|visual & performing arts', r'career', r'world languages|languages other than english',
]


def _is_comprehensive(text):
    """True for full state-standards listings that span most content areas.

    These strings (e.g. Texas TEKS, California frameworks) name 6+ subjects, so
    any single keyword rule would mis-file them. They belong in Cross-subject.
    """
    hits = sum(1 for m in _BREADTH_MARKERS if re.search(m, text))
    return hits >= 4


# (regex, bucket) - evaluated top to bottom, first hit wins.
RULES = [
    # --- Resources whose SUBJECT is language itself ---
    (r'language learning|language acquisition|multilingual|english language learn'
     r'|english language develop|language translation|english language learners'
     r'|world languages|readability', WORLD_LANG),

    # --- Special education / policy / law ---
    (r'special education|educational policy|accessibility|\blaw\b'
     r'|educational statistics|standards\b|administrative', POLICY),

    # --- Career, business, finance ---
    (r'financial literacy|business education|entrepreneurship|career development'
     r'|career & technical|business management', CAREER),

    # --- Computer science / AI / reasoning ---
    (r'computer science|\bai\b|artificial intelligence|reasoning', CS_AI),

    # --- Social studies ---
    (r'social studies|civics|history|geography|economics|politics', SOCIAL),

    # --- Math (before science, so "Mathematics; Physics" reads as math-led) ---
    (r'\bmath\b|mathematics', MATH),

    # --- Science / STEM ---
    (r'science|stem|physics|chemistry|biology|engineering', SCIENCE),

    # --- English language arts / literacy ---
    (r'\bela\b|english language arts|literacy|writing|reading'
     r'|speaking & listening|speaking and listening|grammar|vocabulary', ELA),

    # --- Named non-English languages, checked only AFTER content areas so a
    # --- Turkish math dataset files under Mathematics, not World Languages.
    (r'turkish|korean|german curriculum|indian languages|luganda|kinyarwanda',
     WORLD_LANG),

    # --- Everything else that is explicitly cross-cutting ---
    (r'cross-subject|general|education|tutoring|classroom discourse'
     r'|instructional video|research', GENERAL),
]


def canonicalize(raw):
    """Map one raw subject_area string to a canonical bucket."""
    if not isinstance(raw, str) or not raw.strip():
        return GENERAL
    text = raw.lower()
    # A resource spanning most content areas is cross-subject by definition,
    # regardless of which keyword happens to appear first.
    if _is_comprehensive(text):
        return GENERAL
    for pattern, bucket in RULES:
        if re.search(pattern, text):
            return bucket
    return GENERAL


def main():
    df = pd.read_csv(CSV)
    if 'subject_area' not in df.columns:
        sys.exit('ERROR: subject_area column missing')

    before = df['subject_area'].nunique()
    df['subject_canonical'] = df['subject_area'].apply(canonicalize)

    # Keep the column order stable: put canonical right after subject_area.
    cols = list(df.columns)
    cols.remove('subject_canonical')
    cols.insert(cols.index('subject_area') + 1, 'subject_canonical')
    df = df[cols]

    df.to_csv(CSV, index=False)

    print(f'subject_area distinct values: {before} -> '
          f"{df['subject_canonical'].nunique()} canonical\n")
    counts = df['subject_canonical'].value_counts()
    for bucket in CANONICAL_ORDER:
        if bucket in counts:
            print(f'  {counts[bucket]:4}  {bucket}')

    unexpected = set(df['subject_canonical']) - set(CANONICAL_ORDER)
    if unexpected:
        sys.exit(f'ERROR: unexpected buckets produced: {unexpected}')

    print('\n--- mapping audit (raw -> canonical) ---')
    audit = (df[['subject_area', 'subject_canonical']]
             .drop_duplicates()
             .sort_values(['subject_canonical', 'subject_area']))
    for _, r in audit.iterrows():
        print(f"  {r['subject_canonical'][:34]:34} <- {str(r['subject_area'])[:70]}")


if __name__ == '__main__':
    main()
