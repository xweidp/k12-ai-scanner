#!/usr/bin/env python3
"""
GitHub & Hugging Face Direct Scanner for K-12 AI Datasets

Searches GitHub and Hugging Face directly for K-12 education datasets,
benchmarks, and models with data/artifact evidence.

Complements the generic monitor-source scanner.
"""

import json
import requests
from datetime import datetime, timezone
from pathlib import Path
import os

GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

# Search queries for finding K-12 datasets
GITHUB_QUERIES = [
    "k-12 dataset language:* stars:>10",
    "education dataset k12 language:* stars:>5",
    "student data benchmark language:* stars:>5",
    "learning science dataset language:* stars:>5",
    "math word problem dataset language:*",
    "reading comprehension dataset language:*",
    "science question dataset language:*"
]

HF_QUERIES = [
    "k-12",
    "k12",
    "education dataset",
    "student learning",
    "math word problem",
    "reading comprehension",
    "science reasoning"
]

def search_github_datasets(max_results=100):
    """Search GitHub for K-12 datasets with data artifacts."""
    github_token = os.getenv('GITHUB_TOKEN', '')
    headers = {}
    if github_token:
        headers['Authorization'] = f'token {github_token}'
    else:
        print(f"{YELLOW}ℹ No GITHUB_TOKEN - using public API (rate-limited){RESET}")

    headers['Accept'] = 'application/vnd.github.v3+json'

    resources = []
    checked = set()

    for query in GITHUB_QUERIES:
        try:
            print(f"  Searching GitHub: {query[:40]}...")
            url = f"https://api.github.com/search/repositories?q={query}&sort=stars&per_page=30"

            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"    {YELLOW}Status {response.status_code}{RESET}")
                continue

            data = response.json()
            items = data.get('items', [])

            for item in items[:10]:
                repo_url = item.get('html_url', '')
                if not repo_url or repo_url in checked:
                    continue

                checked.add(repo_url)

                resource = {
                    'id': f"github-{item.get('id')}",
                    'title': item.get('name', ''),
                    'source': 'GitHub',
                    'program': item.get('owner', {}).get('login', ''),
                    'resourceType': 'Dataset',
                    'url': repo_url,
                    'subjects': extract_subjects_from_text(item.get('description', '') + item.get('topics', []).__str__()),
                    'gradeBand': 'K-12',
                    'modality': [],
                    'license': item.get('license', {}).get('name', 'See repository'),
                    'description': item.get('description', '')[:200],
                    'stars': item.get('stargazers_count', 0),
                    'matchedTerms': ['dataset', 'github', 'k-12'],
                    'fit': 40,
                    'addedVia': 'github_scan'
                }
                resources.append(resource)

        except Exception as e:
            print(f"    {RED}Error: {e}{RESET}")

    print(f"{GREEN}✓ Found {len(resources)} GitHub datasets{RESET}")
    return resources

def search_huggingface_datasets(max_results=100):
    """Search Hugging Face for K-12 datasets."""
    resources = []
    checked = set()

    for query in HF_QUERIES:
        try:
            print(f"  Searching Hugging Face: {query}...")

            # HF datasets API
            url = f"https://huggingface.co/api/datasets?search={query}&limit=30"
            response = requests.get(url, timeout=10)

            if response.status_code != 200:
                print(f"    {YELLOW}Status {response.status_code}{RESET}")
                continue

            items = response.json()

            for item in items[:10]:
                dataset_id = item.get('id', '')
                if not dataset_id or dataset_id in checked:
                    continue

                checked.add(dataset_id)

                dataset_url = f"https://huggingface.co/datasets/{dataset_id}"

                resource = {
                    'id': f"hf-{dataset_id.replace('/', '-')}",
                    'title': item.get('id', ''),
                    'source': 'Hugging Face',
                    'program': dataset_id.split('/')[0],
                    'resourceType': 'Dataset',
                    'url': dataset_url,
                    'subjects': extract_subjects_from_text(item.get('description', '') or ''),
                    'gradeBand': 'K-12',
                    'modality': [],
                    'license': item.get('card_data', {}).get('license', 'See repository'),
                    'description': (item.get('description', '') or item.get('card_data', {}).get('summary', ''))[:200],
                    'downloads': item.get('downloads', 0),
                    'likes': item.get('likes', 0),
                    'matchedTerms': ['dataset', 'huggingface', 'k-12'],
                    'fit': 40,
                    'addedVia': 'huggingface_scan'
                }
                resources.append(resource)

        except Exception as e:
            print(f"    {RED}Error: {e}{RESET}")

    print(f"{GREEN}✓ Found {len(resources)} Hugging Face datasets{RESET}")
    return resources

def extract_subjects_from_text(text):
    """Extract subject areas from text."""
    subject_map = {
        'math': ['math', 'mathematics', 'arithmetic', 'word problem'],
        'science': ['science', 'physics', 'chemistry', 'biology'],
        'reading': ['reading', 'comprehension', 'literacy'],
        'writing': ['writing', 'essay', 'text generation'],
        'assessment': ['assessment', 'grading', 'evaluation']
    }

    text_lower = str(text).lower()
    subjects = []

    for subject, keywords in subject_map.items():
        if any(kw in text_lower for kw in keywords):
            subjects.append(subject.capitalize())

    return list(set(subjects)) if subjects else ['General']

def dedupe_with_existing(new_resources, existing_urls):
    """Remove resources already in inventory."""
    deduped = []
    for res in new_resources:
        url = res.get('url', '')
        if not any(url == existing or url in str(existing) for existing in existing_urls):
            deduped.append(res)
    return deduped

def main():
    print(f"\n{GREEN}=== GitHub & Hugging Face Direct Scan ==={RESET}\n")

    # Load existing URLs to avoid duplicates
    existing_urls = set()
    if Path('data/k12_inventory_latest.csv').exists():
        import pandas as pd
        try:
            df = pd.read_csv('data/k12_inventory_latest.csv')
            existing_urls = set(df['url'].dropna().tolist())
            print(f"{GREEN}✓ Loaded {len(existing_urls)} existing URLs{RESET}\n")
        except:
            pass

    # Search GitHub
    print(f"{GREEN}Searching GitHub...{RESET}")
    github_resources = search_github_datasets()
    github_resources = dedupe_with_existing(github_resources, existing_urls)
    print(f"{GREEN}→ {len(github_resources)} new from GitHub{RESET}\n")

    # Search Hugging Face
    print(f"{GREEN}Searching Hugging Face...{RESET}")
    hf_resources = search_huggingface_datasets()
    hf_resources = dedupe_with_existing(hf_resources, existing_urls)
    print(f"{GREEN}→ {len(hf_resources)} new from Hugging Face{RESET}\n")

    # Combine
    all_resources = github_resources + hf_resources

    # Add discovery metadata
    for res in all_resources:
        res['discovery_date'] = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        res['discovery_time'] = datetime.now(timezone.utc).isoformat()

    # Save results
    output = {
        'scannedAt': datetime.now(timezone.utc).isoformat(),
        'source': 'GitHub & Hugging Face direct scan',
        'profile': 'K-12 AI datasets, benchmarks, and models',
        'counts': {
            'github': len(github_resources),
            'huggingface': len(hf_resources),
            'total': len(all_resources)
        },
        'resources': all_resources
    }

    with open('data/github_hf_scan_results.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"{GREEN}✓ Saved {len(all_resources)} new discoveries to data/github_hf_scan_results.json{RESET}")
    print(f"\nSummary:")
    print(f"  GitHub:        {len(github_resources)} new")
    print(f"  Hugging Face:  {len(hf_resources)} new")
    print(f"  Total:         {len(all_resources)} new\n")

    return all_resources

if __name__ == '__main__':
    main()
