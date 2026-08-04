#!/usr/bin/env python3
"""
Scan for K-12 AI education benchmarks from major sources.
Sources: Papers with Code, HuggingFace, ArXiv, GitHub
"""

import pandas as pd
import requests
from datetime import datetime
import time

def scan_papers_with_code_benchmarks():
    """Scan Papers with Code for education benchmarks"""
    results = []
    try:
        url = "https://paperswithcode.com/api/benchmarks/"
        params = {
            'search': 'education',
            'ordering': '-created',
            'page_size': 20
        }
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()

        data = response.json()
        for benchmark in data.get('results', []):
            name = benchmark.get('name', '')
            if any(kw in name.lower() for kw in ['education', 'student', 'school', 'k-12', 'learning', 'teacher', 'math', 'reading']):
                results.append({
                    'resource_name': f"Papers with Code: {name[:80]}",
                    'organization': 'Papers with Code',
                    'announcement_date': datetime.now().strftime('%Y-%m-%d'),
                    'expected_release_date': '',
                    'status': 'Active',
                    'source_url': f"https://paperswithcode.com/benchmark/{name.lower().replace(' ', '-')}",
                    'description': 'Benchmark from Papers with Code',
                    'estimated_size': '',
                    'source_type': 'benchmark',
                    'preview_available': 'Yes',
                    'last_updated': datetime.now().strftime('%Y-%m-%d')
                })
    except Exception as e:
        print(f"  Papers with Code: {e}")

    return results

def scan_arxiv_benchmarks():
    """Scan ArXiv for K-12 AI benchmarks"""
    results = []
    try:
        url = "http://export.arxiv.org/api/query"
        params = {
            'search_query': 'cat:cs.CY AND benchmark AND (education OR student OR school OR "k-12" OR learning)',
            'start': 0,
            'max_results': 20,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()

        import xml.etree.ElementTree as ET
        root = ET.fromstring(response.content)

        for entry in root.findall('{http://www.w3.org/2005/Atom}entry')[:10]:
            title = entry.find('{http://www.w3.org/2005/Atom}title').text
            arxiv_id = entry.find('{http://www.w3.org/2005/Atom}id').text.split('/abs/')[-1]
            published = entry.find('{http://www.w3.org/2005/Atom}published').text[:10]

            results.append({
                'resource_name': f"ArXiv: {title[:80]}",
                'organization': 'ArXiv',
                'announcement_date': published,
                'expected_release_date': '',
                'status': 'Published',
                'source_url': f"https://arxiv.org/abs/{arxiv_id}",
                'description': 'Benchmark from research paper',
                'estimated_size': '',
                'source_type': 'benchmark',
                'preview_available': 'Yes',
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            })
    except Exception as e:
        print(f"  ArXiv: {e}")

    return results

def scan_huggingface_benchmarks():
    """Scan HuggingFace for education benchmarks"""
    results = []
    try:
        url = "https://huggingface.co/api/datasets"
        params = {'full': True, 'limit': 30}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        datasets = response.json()

        for ds in datasets[:15]:
            name = ds.get('id', '')
            desc = (ds.get('description') or '').lower()

            # Look for benchmarks specifically
            if any(kw in desc for kw in ['benchmark', 'evaluation']) and any(kw in desc for kw in ['education', 'student', 'school', 'k-12', 'learning']):
                results.append({
                    'resource_name': f"HuggingFace Benchmark: {name[:80]}",
                    'organization': 'HuggingFace',
                    'announcement_date': datetime.now().strftime('%Y-%m-%d'),
                    'expected_release_date': '',
                    'status': 'Available',
                    'source_url': f"https://huggingface.co/datasets/{name}",
                    'description': (ds.get('description', '') or '')[:150],
                    'estimated_size': '',
                    'source_type': 'benchmark',
                    'preview_available': 'Yes',
                    'last_updated': datetime.now().strftime('%Y-%m-%d')
                })
    except Exception as e:
        print(f"  HuggingFace: {e}")

    return results

def scan_github_benchmarks():
    """Scan GitHub for education benchmarks"""
    results = []
    repos = [
        'allenai/allennlp',
        'huggingface/datasets',
        'pytorch/pytorch',
    ]

    try:
        for repo in repos:
            url = f"https://api.github.com/repos/{repo}/releases"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                releases = response.json()[:5]
                for rel in releases:
                    body = (rel.get('body') or '').lower()
                    if any(kw in body for kw in ['benchmark', 'evaluation']) and any(kw in body for kw in ['education', 'student', 'school']):
                        results.append({
                            'resource_name': f"GitHub: {repo.split('/')[1]} Benchmark",
                            'organization': f"GitHub - {repo.split('/')[0]}",
                            'announcement_date': rel.get('published_at', '')[:10],
                            'expected_release_date': '',
                            'status': 'Released',
                            'source_url': rel.get('html_url', ''),
                            'description': 'Benchmark from GitHub release',
                            'estimated_size': '',
                            'source_type': 'benchmark',
                            'preview_available': 'Yes',
                            'last_updated': datetime.now().strftime('%Y-%m-%d')
                        })
    except Exception as e:
        print(f"  GitHub: {e}")

    return results

def main():
    print("🔍 Scanning for K-12 AI education benchmarks...\n")

    all_results = []

    # 1. Papers with Code
    print("📊 Papers with Code benchmarks...")
    all_results.extend(scan_papers_with_code_benchmarks())

    # 2. ArXiv
    print("📝 ArXiv benchmarks...")
    all_results.extend(scan_arxiv_benchmarks())

    # 3. HuggingFace
    print("🤗 HuggingFace benchmarks...")
    all_results.extend(scan_huggingface_benchmarks())

    # 4. GitHub
    print("🐙 GitHub benchmarks...")
    all_results.extend(scan_github_benchmarks())

    # Deduplicate
    seen_urls = set()
    unique_results = []
    for row in all_results:
        url = row.get('source_url', '')
        if url not in seen_urls:
            unique_results.append(row)
            seen_urls.add(url)

    # Save
    if unique_results:
        df = pd.DataFrame(unique_results)
        df.to_csv('data/k12_benchmarks_discovered.csv', index=False)
        print(f"\n✅ Found {len(df)} K-12 AI education benchmarks\n")
        for _, row in df.head(10).iterrows():
            print(f"     → {row['resource_name'][:80]}")
    else:
        print("\n⚠️  No new benchmarks found this scan")

if __name__ == '__main__':
    main()
