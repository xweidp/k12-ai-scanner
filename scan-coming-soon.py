#!/usr/bin/env python3
"""
Scan for upcoming K-12 AI datasets from multiple sources.
Simplified prototype version with inline scanners.
"""

import pandas as pd
import requests
from datetime import datetime
import time
import json

def scan_drivendata():
    """Scrape DrivenData competitions"""
    results = []
    try:
        url = "https://www.drivendata.org/competitions/"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Simple extraction - look for competition links
        if 'competition' in response.text.lower():
            results.append({
                'resource_name': 'DrivenData Education Competitions',
                'organization': 'DrivenData',
                'announcement_date': datetime.now().strftime('%Y-%m-%d'),
                'expected_release_date': '',
                'status': 'Active',
                'source_url': url,
                'description': 'Browse current and upcoming data competitions',
                'estimated_size': '',
                'source_type': 'competition',
                'preview_available': 'Yes',
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            })
    except Exception as e:
        print(f"  DrivenData: {e}")

    return results

def scan_k12_infrastructure():
    """Scan K-12 AI Infrastructure"""
    results = []
    try:
        url = "https://platform.k12-ai-infrastructure.org/datasets/"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        if 'dataset' in response.text.lower():
            results.append({
                'resource_name': 'K-12 AI Infrastructure Datasets',
                'organization': 'K-12 AI Infrastructure',
                'announcement_date': datetime.now().strftime('%Y-%m-%d'),
                'expected_release_date': '',
                'status': 'Available',
                'source_url': url,
                'description': 'Official K-12 AI datasets and resources platform',
                'estimated_size': '',
                'source_type': 'platform',
                'preview_available': 'Yes',
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            })
    except Exception as e:
        print(f"  K-12 Infrastructure: {e}")

    return results

def scan_ldc_upenn():
    """Scan LDC UPenn"""
    results = []
    try:
        url = "https://www.ldc.upenn.edu/language-resources/data-sets"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        if 'dataset' in response.text.lower():
            results.append({
                'resource_name': 'LDC UPenn Linguistic Datasets',
                'organization': 'LDC UPenn',
                'announcement_date': datetime.now().strftime('%Y-%m-%d'),
                'expected_release_date': '',
                'status': 'Available',
                'source_url': url,
                'description': 'Linguistic Data Consortium datasets for education',
                'estimated_size': '',
                'source_type': 'linguistic_data',
                'preview_available': 'Yes',
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            })
    except Exception as e:
        print(f"  LDC: {e}")

    return results

def scan_github_k12ai():
    """Monitor GitHub for K-12 AI releases"""
    results = []
    repos = [
        'xweidp/k12-ai-scanner',
        'allenai/ai2-education',
    ]

    for repo in repos:
        try:
            url = f"https://api.github.com/repos/{repo}/releases"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            releases = response.json()
            if releases and len(releases) > 0:
                latest = releases[0]
                results.append({
                    'resource_name': f"{repo}: {latest.get('name', 'Latest Release')}",
                    'organization': f"GitHub - {repo.split('/')[0]}",
                    'announcement_date': latest.get('published_at', '')[:10],
                    'expected_release_date': '',
                    'status': 'Released',
                    'source_url': latest.get('html_url', ''),
                    'description': (latest.get('body', '') or '')[:200],
                    'estimated_size': '',
                    'source_type': 'github_release',
                    'preview_available': 'Yes',
                    'last_updated': datetime.now().strftime('%Y-%m-%d')
                })
        except Exception as e:
            print(f"  GitHub {repo}: {e}")

    return results

def scan_nsf_announcements():
    """Scan NSF for education grants"""
    results = []
    try:
        url = "https://www.nsf.gov/funding/programs/"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        if 'education' in response.text.lower() and 'grant' in response.text.lower():
            results.append({
                'resource_name': 'NSF Education AI Funding Opportunities',
                'organization': 'National Science Foundation',
                'announcement_date': datetime.now().strftime('%Y-%m-%d'),
                'expected_release_date': '',
                'status': 'Open for Applications',
                'source_url': url,
                'description': 'NSF funding programs for K-12 AI education and datasets',
                'estimated_size': '',
                'source_type': 'government_grant',
                'preview_available': 'Yes',
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            })
    except Exception as e:
        print(f"  NSF: {e}")

    return results

def main():
    print("Scanning for upcoming K-12 AI datasets...\n")

    all_results = []

    print("📊 Scanning DrivenData...")
    all_results.extend(scan_drivendata())

    print("📚 Scanning K-12 AI Infrastructure...")
    all_results.extend(scan_k12_infrastructure())

    print("🔤 Scanning LDC UPenn...")
    all_results.extend(scan_ldc_upenn())

    print("🐙 Scanning GitHub K-12 AI projects...")
    all_results.extend(scan_github_k12ai())

    print("🏛️  Scanning NSF announcements...")
    all_results.extend(scan_nsf_announcements())

    # Deduplicate by URL
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
        df.to_csv('data/k12_datasets_coming_soon.csv', index=False)
        print(f"\n✅ Found {len(df)} upcoming K-12 AI resources")
        print(f"   Breakdown by source:")
        for source, count in df['source_type'].value_counts().items():
            print(f"     - {source}: {count}")
    else:
        print("\n⚠️  No results found")

if __name__ == '__main__':
    main()
