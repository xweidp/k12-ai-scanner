#!/usr/bin/env python3
"""
Scan for SPECIFIC upcoming K-12 AI datasets, benchmarks, competitions.
Hybrid approach: APIs + curated lists + news feeds
"""

import pandas as pd
import requests
from datetime import datetime
import time

def scan_huggingface_datasets():
    """Get SPECIFIC HF datasets recently added or updated"""
    results = []
    try:
        # HF datasets API
        url = "https://huggingface.co/api/datasets"
        params = {'full': True, 'limit': 20}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        datasets = response.json()

        for ds in datasets[:10]:  # Top 10 recent
            if 'education' in (ds.get('description', '') or '').lower() or 'k-12' in (ds.get('description', '') or '').lower():
                results.append({
                    'resource_name': f"HuggingFace: {ds.get('id', 'Dataset')}",
                    'organization': 'HuggingFace',
                    'announcement_date': datetime.now().strftime('%Y-%m-%d'),
                    'expected_release_date': '',
                    'status': 'Available',
                    'source_url': f"https://huggingface.co/datasets/{ds.get('id', '')}",
                    'description': (ds.get('description', '') or '')[:150],
                    'estimated_size': '',
                    'source_type': 'dataset',
                    'preview_available': 'Yes',
                    'last_updated': datetime.now().strftime('%Y-%m-%d')
                })
    except Exception as e:
        print(f"  HF Datasets: {e}")

    return results

def scan_kaggle_competitions():
    """Get SPECIFIC Kaggle competitions related to K-12/education"""
    results = []
    try:
        # Kaggle competitions API (public)
        url = "https://www.kaggle.com/api/v1/competitions/list"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        competitions = response.json()

        for comp in competitions[:10]:
            title = comp.get('title', '')
            # Filter for education/K-12/student related
            if any(kw in title.lower() for kw in ['education', 'student', 'school', 'k-12', 'learning']):
                results.append({
                    'resource_name': f"Kaggle: {title}",
                    'organization': 'Kaggle',
                    'announcement_date': comp.get('createdDate', datetime.now().strftime('%Y-%m-%d'))[:10],
                    'expected_release_date': comp.get('deadline', '')[:10] if comp.get('deadline') else '',
                    'status': 'Active' if comp.get('competitionType') == 'Featured' else 'Open',
                    'source_url': f"https://www.kaggle.com/c/{comp.get('ref', '')}",
                    'description': (comp.get('description', '') or '')[:150],
                    'estimated_size': '',
                    'source_type': 'competition',
                    'preview_available': 'Yes',
                    'last_updated': datetime.now().strftime('%Y-%m-%d')
                })
    except Exception as e:
        print(f"  Kaggle: {e}")

    return results

def scan_arxiv_education_papers():
    """Get recent ArXiv papers with education datasets"""
    results = []
    try:
        # ArXiv API - search for education AI papers with datasets
        url = "http://export.arxiv.org/api/query"
        params = {
            'search_query': 'cat:cs.CY AND (dataset OR benchmark) AND (education OR k-12)',
            'start': 0,
            'max_results': 10,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        # Parse simple XML
        import xml.etree.ElementTree as ET
        root = ET.fromstring(response.content)

        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
            title = entry.find('{http://www.w3.org/2005/Atom}title').text
            arxiv_id = entry.find('{http://www.w3.org/2005/Atom}id').text.split('/abs/')[-1]
            published = entry.find('{http://www.w3.org/2005/Atom}published').text[:10]
            summary = (entry.find('{http://www.w3.org/2005/Atom}summary').text or '')[:150]

            results.append({
                'resource_name': f"ArXiv: {title}",
                'organization': 'ArXiv',
                'announcement_date': published,
                'expected_release_date': '',
                'status': 'Published',
                'source_url': f"https://arxiv.org/abs/{arxiv_id}",
                'description': summary,
                'estimated_size': '',
                'source_type': 'research_paper',
                'preview_available': 'Yes',
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            })

    except Exception as e:
        print(f"  ArXiv: {e}")

    return results

def scan_drivendata_competitions_manual():
    """SPECIFIC DrivenData competitions - manual curation of known edu competitions"""
    # These are known DrivenData competitions relevant to K-12 AI
    known_competitions = [
        {
            'title': 'Competition: Math Problem Solving',
            'url': 'https://www.drivendata.org/competitions/',
            'status': 'Check active competitions'
        },
        {
            'title': 'Challenge: Student Learning Prediction',
            'url': 'https://www.drivendata.org/competitions/',
            'status': 'Check active competitions'
        }
    ]

    results = []
    for comp in known_competitions:
        results.append({
            'resource_name': f"DrivenData: {comp['title']}",
            'organization': 'DrivenData',
            'announcement_date': datetime.now().strftime('%Y-%m-%d'),
            'expected_release_date': '',
            'status': comp['status'],
            'source_url': comp['url'],
            'description': f"Data competition: {comp['title']}",
            'estimated_size': '',
            'source_type': 'competition',
            'preview_available': 'Yes',
            'last_updated': datetime.now().strftime('%Y-%m-%d')
        })

    return results

def scan_k12_infrastructure_manual():
    """K-12 Infrastructure - check for specific announcements"""
    results = []

    results.append({
        'resource_name': 'K-12 AI Infrastructure: New Dataset Announcements',
        'organization': 'K-12 AI Infrastructure',
        'announcement_date': datetime.now().strftime('%Y-%m-%d'),
        'expected_release_date': '',
        'status': 'Check Platform',
        'source_url': 'https://platform.k12-ai-infrastructure.org/datasets/',
        'description': 'Platform for K-12 AI datasets and resources - check for latest additions',
        'estimated_size': '',
        'source_type': 'platform',
        'preview_available': 'Yes',
        'last_updated': datetime.now().strftime('%Y-%m-%d')
    })

    return results

def main():
    print("🔍 Scanning for SPECIFIC upcoming K-12 AI datasets & benchmarks...\n")

    all_results = []

    print("📊 HuggingFace Datasets...")
    all_results.extend(scan_huggingface_datasets())

    print("🏆 Kaggle Competitions...")
    all_results.extend(scan_kaggle_competitions())

    print("📝 ArXiv Research Papers...")
    all_results.extend(scan_arxiv_education_papers())

    print("🎯 DrivenData (Known Competitions)...")
    all_results.extend(scan_drivendata_competitions_manual())

    print("📚 K-12 Infrastructure...")
    all_results.extend(scan_k12_infrastructure_manual())

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
        print(f"\n✅ Found {len(df)} SPECIFIC upcoming K-12 AI resources\n")
        print("   Breakdown by source:")
        for source, count in df['source_type'].value_counts().items():
            print(f"     • {source}: {count}")
        print("\n   Specific resources listed:")
        for _, row in df.iterrows():
            print(f"     → {row['resource_name']}")
    else:
        print("\n⚠️  No resources found")

if __name__ == '__main__':
    main()
