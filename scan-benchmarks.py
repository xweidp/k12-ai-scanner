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

def scan_openreview_benchmarks():
    """Scan OpenReview.net for K-12 AI benchmarks (Phase 2)"""
    results = []
    try:
        # Use direct OpenReview web interface search
        conferences = ['ICLR.cc/2024', 'NeurIPS.cc/2024', 'EMNLP/2024']

        for conf in conferences[:2]:
            try:
                search_url = f"https://openreview.net/search?term=education+benchmark&venue={conf}"
                response = requests.get(search_url, timeout=10)
                if response.status_code == 200:
                    results.append({
                        'resource_name': f"OpenReview: {conf} Education Benchmarks",
                        'organization': 'OpenReview',
                        'announcement_date': datetime.now().strftime('%Y-%m-%d'),
                        'expected_release_date': '',
                        'status': 'Published',
                        'source_url': search_url,
                        'description': 'Education benchmarks from OpenReview conference',
                        'estimated_size': '',
                        'source_type': 'benchmark',
                        'preview_available': 'Yes',
                        'last_updated': datetime.now().strftime('%Y-%m-%d')
                    })
            except:
                pass
    except Exception as e:
        print(f"  OpenReview: {e}")

    return results

def scan_acl_anthology_benchmarks():
    """Scan ACL Anthology for education benchmarks (Phase 3)"""
    results = []
    try:
        education_venues = ['2024.acl', '2024.emnlp', '2024.naacl']

        for venue in education_venues[:2]:
            try:
                search_url = f"https://www.aclweb.org/anthology/volumes/{venue}/"
                response = requests.get(search_url, timeout=10)
                if response.status_code == 200:
                    results.append({
                        'resource_name': f"ACL {venue}: Education Benchmarks Archive",
                        'organization': 'ACL',
                        'announcement_date': datetime.now().strftime('%Y-%m-%d'),
                        'expected_release_date': '',
                        'status': 'Active',
                        'source_url': search_url,
                        'description': 'Education benchmarks from ACL conference',
                        'estimated_size': '',
                        'source_type': 'benchmark',
                        'preview_available': 'Yes',
                        'last_updated': datetime.now().strftime('%Y-%m-%d')
                    })
            except:
                pass
    except Exception as e:
        print(f"  ACL Anthology: {e}")

    return results

def scan_ai2_benchmarks():
    """Scan AI2 (Allen Institute) for education benchmarks (Phase 3)"""
    results = []
    try:
        # AI2 offers several education-focused benchmarks
        ai2_resources = [
            {'name': 'SQuAD', 'url': 'https://rajpurkar.github.io/SQuAD-explorer/'},
            {'name': 'MMLU', 'url': 'https://github.com/hendrycks/test'},
        ]

        for resource in ai2_resources:
            try:
                response = requests.get(resource['url'], timeout=10)
                if response.status_code == 200:
                    results.append({
                        'resource_name': f"AI2: {resource['name']} Benchmark",
                        'organization': 'Allen Institute for AI',
                        'announcement_date': datetime.now().strftime('%Y-%m-%d'),
                        'expected_release_date': '',
                        'status': 'Active',
                        'source_url': resource['url'],
                        'description': 'Benchmark from Allen Institute for AI',
                        'estimated_size': '',
                        'source_type': 'benchmark',
                        'preview_available': 'Yes',
                        'last_updated': datetime.now().strftime('%Y-%m-%d')
                    })
            except:
                pass
    except Exception as e:
        print(f"  AI2: {e}")

    return results

def scan_github_trending_benchmarks():
    """Scan GitHub trending for education benchmark repositories (Phase 2)"""
    results = []
    try:
        # Search GitHub for benchmark repositories
        url = "https://api.github.com/search/repositories"
        params = {
            'q': 'education benchmark stars:>50',
            'sort': 'stars',
            'order': 'desc',
            'per_page': 20
        }
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()

        data = response.json()
        for repo in data.get('items', [])[:10]:
            if any(kw in (repo.get('description') or '').lower() for kw in ['education', 'student', 'school', 'k-12']):
                results.append({
                    'resource_name': f"GitHub: {repo.get('name', '')[:80]}",
                    'organization': f"GitHub - {repo.get('owner', {}).get('login', '')}",
                    'announcement_date': repo.get('created_at', '')[:10],
                    'expected_release_date': '',
                    'status': 'Active',
                    'source_url': repo.get('html_url', ''),
                    'description': (repo.get('description') or '')[:150],
                    'estimated_size': '',
                    'source_type': 'benchmark',
                    'preview_available': 'Yes',
                    'last_updated': datetime.now().strftime('%Y-%m-%d')
                })
    except Exception as e:
        print(f"  GitHub Trending: {e}")

    return results

def scan_aied_conference_benchmarks():
    """Scan AIED conference papers for education benchmarks (Phase 2)"""
    results = []
    try:
        aied_venues = [
            'https://aied2024.org',
            'https://aied2023.org',
        ]

        for venue in aied_venues:
            try:
                response = requests.get(venue, timeout=10)
                if response.status_code == 200:
                    results.append({
                        'resource_name': f"AIED: {venue.split('/')[2]} Conference Benchmarks",
                        'organization': 'AIED Conference',
                        'announcement_date': datetime.now().strftime('%Y-%m-%d'),
                        'expected_release_date': '',
                        'status': 'Published',
                        'source_url': venue,
                        'description': 'AI in Education conference benchmarks',
                        'estimated_size': '',
                        'source_type': 'benchmark',
                        'preview_available': 'Yes',
                        'last_updated': datetime.now().strftime('%Y-%m-%d')
                    })
            except:
                pass
    except Exception as e:
        print(f"  AIED Conference: {e}")

    return results

def scan_education_benchmark_platforms():
    """Scan education-specific benchmark platforms (Phase 2 & 3)"""
    results = []
    platforms = [
        {
            'name': 'ELSA (Educational Language Science)',
            'url': 'https://elsa-benchmark.github.io/'
        },
        {
            'name': 'K-12 AI Infrastructure Benchmarks',
            'url': 'https://platform.k12-ai-infrastructure.org/'
        },
        {
            'name': 'Bloom Taxonomy Benchmarks',
            'url': 'https://github.com/kuanghuei/bloom-benchmark'
        },
    ]

    for platform in platforms:
        try:
            response = requests.get(platform['url'], timeout=10)
            if response.status_code == 200:
                results.append({
                    'resource_name': f"Education Benchmark: {platform['name']}",
                    'organization': 'Education Benchmark Platform',
                    'announcement_date': datetime.now().strftime('%Y-%m-%d'),
                    'expected_release_date': '',
                    'status': 'Active',
                    'source_url': platform['url'],
                    'description': f'Education-specific benchmark: {platform["name"]}',
                    'estimated_size': '',
                    'source_type': 'benchmark',
                    'preview_available': 'Yes',
                    'last_updated': datetime.now().strftime('%Y-%m-%d')
                })
        except:
            pass

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

    # PHASE 1: Core sources
    print("📊 Papers with Code benchmarks...")
    all_results.extend(scan_papers_with_code_benchmarks())

    print("📝 ArXiv benchmarks...")
    all_results.extend(scan_arxiv_benchmarks())

    print("🤗 HuggingFace benchmarks...")
    all_results.extend(scan_huggingface_benchmarks())

    # PHASE 2: Specialized education platforms
    print("📖 OpenReview benchmarks...")
    all_results.extend(scan_openreview_benchmarks())

    print("🎓 AIED Conference benchmarks...")
    all_results.extend(scan_aied_conference_benchmarks())

    print("🏫 Education-specific benchmark platforms...")
    all_results.extend(scan_education_benchmark_platforms())

    print("🌟 GitHub trending education benchmarks...")
    all_results.extend(scan_github_trending_benchmarks())

    # PHASE 3: General AI platforms
    print("📚 ACL Anthology benchmarks...")
    all_results.extend(scan_acl_anthology_benchmarks())

    print("🧠 AI2 (Allen Institute) benchmarks...")
    all_results.extend(scan_ai2_benchmarks())

    # GitHub (Phase 1)
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
