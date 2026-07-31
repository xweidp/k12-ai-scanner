#!/usr/bin/env python3
"""
K-12 AI Resource Scanner (Python version)
Fetches, parses, scores K-12 datasets, benchmarks, and models from education sources.
"""

import json
import re
import requests
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse
from html.parser import HTMLParser

# Scoring vocabulary
PROFILE_TERMS = [
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
]

USER_AGENT = "K12ResourceScanner/1.0"

def clean_html(text):
    """Remove HTML tags and decode entities."""
    text = re.sub(r'<[^>]+>', ' ', str(text))
    text = text.replace('&amp;', '&').replace('&nbsp;', ' ').replace('&quot;', '"')
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_links(html, base_url):
    """Extract links from HTML."""
    links = []
    pattern = r'<a\b[^>]*href=["\'](.*?)["\'][^>]*>(.*?)</a>'
    for match in re.finditer(pattern, html, re.IGNORECASE):
        href = match.group(1)
        title = clean_html(match.group(2))
        try:
            url = urljoin(base_url, href)
            if title and len(title) >= 3:
                links.append({'title': title, 'url': url})
        except:
            pass
    return links

def fetch_source(url):
    """Fetch content from a URL."""
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"  ! Error fetching {url}: {e}")
        return None

def detect_subjects(text):
    """Detect education subjects from text."""
    subject_terms = {
        'Math': ['math', 'mathematics', 'arithmetic', 'word problem', 'gsm', 'algebra', 'geometry'],
        'Science': ['science', 'scientific', 'physics', 'chemistry', 'biology', 'sciq'],
        'Reading': ['reading', 'comprehension', 'fairytale', 'narrative'],
        'Writing': ['writing', 'essay', 'argumentative', 'lexical'],
        'Literacy': ['literacy'],
        'Tutoring': ['tutoring', 'tutor', 'dialogue'],
        'Assessment': ['assessment', 'grading', 'scoring', 'rubric'],
        'Classroom discourse': ['classroom', 'transcript', 'discursive', 'talk moves']
    }

    haystack = text.lower()
    subjects = []
    for subject, terms in subject_terms.items():
        if any(term in haystack for term in terms):
            subjects.append(subject)
    return list(set(subjects))

def classify_resource_type(text):
    """Classify resource as Dataset, Benchmark, Model, or Competition."""
    haystack = text.lower()
    if any(word in haystack for word in ['model', 'llm', 'fine-tuned', 'pretrained', 'checkpoint']):
        return 'Model'
    if any(word in haystack for word in ['benchmark', 'bench', 'leaderboard', 'eval', 'multiple-choice', 'graded']):
        return 'Benchmark'
    if 'competition' in haystack or 'challenge' in haystack:
        return 'Competition'
    return 'Dataset'

def score_resource(item):
    """Score resource for K-12 relevance."""
    haystack = f"{item['title']} {item['source']} {item['description']}".lower()
    matched = [term for term in PROFILE_TERMS if term in haystack]

    catalog_boost = 18 if item.get('addedVia') == 'catalog' else 0
    k12_boost = 14 if any(k in haystack for k in ['k-12', 'k-?12', 'grade school', 'elementary', 'classroom']) else 0
    subject_boost = 10 if item.get('subjects') else 0
    type_boost = 8 if any(t in haystack for t in ['dataset', 'benchmark', 'model']) else 0

    fit = min(100, max(0, round(20 + len(matched) * 3 + catalog_boost + k12_boost + subject_boost + type_boost)))
    return {**item, 'matchedTerms': matched[:8], 'fit': fit}

def scan_monitor_source(source):
    """Scan a monitor source for relevant links."""
    html = fetch_source(source['url'])
    if not html:
        return []

    links = extract_links(html, source['url'])
    skip_pattern = r'(skip to|sign in|log in|privacy|contact|newsletter|twitter|facebook|donate|careers|home$|menu)'

    resources = []
    keywords = source.get('keywords', [])

    for i, link in enumerate(links[:25]):
        title = link['title']
        url = link['url']
        haystack = f"{title} {url}".lower()

        # Skip irrelevant links
        if re.search(skip_pattern, haystack, re.IGNORECASE):
            continue

        # Check keyword match
        keyword_match = any(kw.lower() in haystack for kw in keywords)
        if not keyword_match and source.get('linkPattern'):
            if not re.search(source['linkPattern'], url):
                continue
        elif not keyword_match:
            continue

        context = f"{title} {source['name']}"
        resources.append({
            'id': f"monitor-{source['name'].lower().replace(' ', '-')}-{i}",
            'title': title,
            'source': source['name'],
            'program': source['name'],
            'sourceType': source['type'],
            'resourceType': classify_resource_type(context),
            'url': url,
            'subjects': detect_subjects(context),
            'gradeBand': 'K-12',
            'modality': [],
            'license': 'See source',
            'description': f"{source['type']} lead from {source['name']}.",
            'addedVia': 'monitor'
        })

    return resources

def main():
    print("Starting K-12 AI resource scan...")

    # Load watchlist
    watchlist_path = Path('data/source-watchlist.json')
    with open(watchlist_path) as f:
        watchlist = json.load(f)

    collected = []

    for source in watchlist['sources']:
        print(f"Scanning {source['name']}...")

        if source.get('mode') == 'monitor':
            resources = scan_monitor_source(source)
            print(f"  -> {len(resources)} items found")
            collected.extend(resources)
        else:
            print(f"  (catalog mode - requires parser, skipping in quick scan)")

    # Score and sort
    resources = [score_resource(r) for r in collected]
    resources = sorted(resources, key=lambda x: (-x['fit'], x['title']))

    # Write output
    scanned_at = datetime.utcnow().isoformat() + 'Z'
    payload = {
        'scannedAt': scanned_at,
        'source': 'K-12 AI resource watchlist (monitor sources)',
        'profile': 'K-12 AI datasets, benchmarks, and models',
        'counts': {
            'total': len(resources),
            'datasets': len([r for r in resources if r['resourceType'] == 'Dataset']),
            'benchmarks': len([r for r in resources if r['resourceType'] == 'Benchmark']),
            'models': len([r for r in resources if r['resourceType'] == 'Model']),
            'competitions': len([r for r in resources if r['resourceType'] == 'Competition'])
        },
        'resources': resources
    }

    Path('data').mkdir(exist_ok=True)
    with open('data/resources.json', 'w') as f:
        json.dump(payload, f, indent=2)

    print(f"\n✅ Found {len(resources)} resources!")
    print(f"   - {payload['counts']['datasets']} Datasets")
    print(f"   - {payload['counts']['benchmarks']} Benchmarks")
    print(f"   - {payload['counts']['models']} Models")
    print(f"   - {payload['counts']['competitions']} Competitions")
    print(f"\nResults written to data/resources.json")

if __name__ == '__main__':
    main()
