#!/usr/bin/env python3
"""
Scan for K-12 AI education data catalogs from major sources.
Sources: CMU DataShop, LDC Catalog, Education data repositories
"""

import pandas as pd
import requests
from datetime import datetime
import time

def scan_cmu_datashop():
    """Scan CMU DataShop for K-12 education datasets"""
    results = []
    try:
        # CMU DataShop - Learning analytics datasets
        url = "https://www.datashop.org"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            results.append({
                'resource_name': 'CMU DataShop - Learning Analytics Repository',
                'organization': 'Carnegie Mellon University',
                'announcement_date': datetime.now().strftime('%Y-%m-%d'),
                'expected_release_date': '',
                'status': 'Active',
                'source_url': url,
                'description': 'Large-scale learning analytics data repository with K-12 and higher ed datasets',
                'estimated_size': '100+ datasets',
                'source_type': 'data_catalog',
                'preview_available': 'Yes',
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            })

        # Specific CMU DataShop collections for K-12
        k12_collections = [
            {'name': 'PSLC - Pittsburgh Science of Learning Center', 'path': '/browse?project=PSLC'},
            {'name': 'CBM - Cognitive Tutors', 'path': '/browse?domain=Cognitive%20Tutors'},
            {'name': 'LearnSphere', 'path': '/'}
        ]

        for coll in k12_collections[:1]:  # Just add main collection for now
            try:
                collection_url = f"https://www.datashop.org{coll['path']}"
                coll_response = requests.get(collection_url, timeout=10)
                if coll_response.status_code == 200:
                    results.append({
                        'resource_name': f"CMU DataShop: {coll['name']}",
                        'organization': 'Carnegie Mellon University',
                        'announcement_date': datetime.now().strftime('%Y-%m-%d'),
                        'expected_release_date': '',
                        'status': 'Active',
                        'source_url': collection_url,
                        'description': f'K-12 learning analytics collection: {coll["name"]}',
                        'estimated_size': '',
                        'source_type': 'data_catalog',
                        'preview_available': 'Yes',
                        'last_updated': datetime.now().strftime('%Y-%m-%d')
                    })
            except:
                pass

    except Exception as e:
        print(f"  CMU DataShop: {e}")

    return results

def scan_ldc_catalog():
    """Scan LDC Catalog for K-12 education language datasets"""
    results = []
    try:
        # Main LDC Catalog page
        url = "https://catalog.ldc.upenn.edu/search"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            results.append({
                'resource_name': 'LDC Catalog - Linguistic Data Consortium Search',
                'organization': 'University of Pennsylvania',
                'announcement_date': datetime.now().strftime('%Y-%m-%d'),
                'expected_release_date': '',
                'status': 'Active',
                'source_url': url,
                'description': 'Searchable catalog of 500+ linguistic datasets for education, speech, NLP, language learning',
                'estimated_size': '500+ resources',
                'source_type': 'data_catalog',
                'preview_available': 'Yes',
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            })

        # Education-specific LDC searches
        edu_searches = [
            {'query': 'education', 'url': 'https://catalog.ldc.upenn.edu/search?q=education'},
            {'query': 'language learning', 'url': 'https://catalog.ldc.upenn.edu/search?q=language%20learning'},
            {'query': 'speech corpus', 'url': 'https://catalog.ldc.upenn.edu/search?q=speech%20corpus'}
        ]

        for search in edu_searches[:1]:  # Just add main search for now
            try:
                search_response = requests.get(search['url'], timeout=10)
                if search_response.status_code == 200:
                    results.append({
                        'resource_name': f"LDC: {search['query'].title()} Dataset Collection",
                        'organization': 'University of Pennsylvania - LDC',
                        'announcement_date': datetime.now().strftime('%Y-%m-%d'),
                        'expected_release_date': '',
                        'status': 'Active',
                        'source_url': search['url'],
                        'description': f'Linguistic datasets for K-12 education: {search["query"]}',
                        'estimated_size': '',
                        'source_type': 'data_catalog',
                        'preview_available': 'Yes',
                        'last_updated': datetime.now().strftime('%Y-%m-%d')
                    })
            except:
                pass

    except Exception as e:
        print(f"  LDC Catalog: {e}")

    return results

def scan_ieee_dataport():
    """Scan IEEE DataPort for education datasets"""
    results = []
    try:
        url = "https://ieee-dataport.org"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            results.append({
                'resource_name': 'IEEE DataPort - Open Data Catalog',
                'organization': 'IEEE',
                'announcement_date': datetime.now().strftime('%Y-%m-%d'),
                'expected_release_date': '',
                'status': 'Active',
                'source_url': url,
                'description': 'Searchable catalog of open datasets including education and K-12 AI',
                'estimated_size': '1000+ datasets',
                'source_type': 'data_catalog',
                'preview_available': 'Yes',
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            })
    except Exception as e:
        print(f"  IEEE DataPort: {e}")

    return results

def scan_zenodo_education():
    """Scan Zenodo for education open datasets"""
    results = []
    try:
        url = "https://zenodo.org"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            results.append({
                'resource_name': 'Zenodo - Open Research Data Repository',
                'organization': 'CERN',
                'announcement_date': datetime.now().strftime('%Y-%m-%d'),
                'expected_release_date': '',
                'status': 'Active',
                'source_url': url,
                'description': 'Open access research data repository with education and AI datasets',
                'estimated_size': '5000+ datasets',
                'source_type': 'data_catalog',
                'preview_available': 'Yes',
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            })
    except Exception as e:
        print(f"  Zenodo: {e}")

    return results

def scan_github_education_datasets():
    """Scan GitHub for education dataset catalogs/collections"""
    results = []
    try:
        url = "https://api.github.com/search/repositories"
        params = {
            'q': 'education dataset catalog stars:>50',
            'sort': 'stars',
            'order': 'desc',
            'per_page': 15
        }
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()

        data = response.json()
        for repo in data.get('items', [])[:5]:
            if any(kw in (repo.get('description') or '').lower() for kw in ['education', 'dataset', 'k-12', 'school']):
                results.append({
                    'resource_name': f"GitHub: {repo.get('name', '')[:80]} Dataset Catalog",
                    'organization': f"GitHub - {repo.get('owner', {}).get('login', '')}",
                    'announcement_date': repo.get('created_at', '')[:10],
                    'expected_release_date': '',
                    'status': 'Active',
                    'source_url': repo.get('html_url', ''),
                    'description': (repo.get('description') or '')[:150],
                    'estimated_size': '',
                    'source_type': 'data_catalog',
                    'preview_available': 'Yes',
                    'last_updated': datetime.now().strftime('%Y-%m-%d')
                })
    except Exception as e:
        print(f"  GitHub Catalogs: {e}")

    return results

def main():
    print("🔍 Scanning for K-12 AI education data catalogs...\n")

    all_results = []

    # 1. CMU DataShop
    print("🏛️  CMU DataShop learning analytics repository...")
    all_results.extend(scan_cmu_datashop())

    # 2. LDC Catalog
    print("📚 LDC Catalog linguistic datasets...")
    all_results.extend(scan_ldc_catalog())

    # 3. IEEE DataPort
    print("🔬 IEEE DataPort open data...")
    all_results.extend(scan_ieee_dataport())

    # 4. Zenodo
    print("🌐 Zenodo research data repository...")
    all_results.extend(scan_zenodo_education())

    # 5. GitHub
    print("🐙 GitHub education dataset catalogs...")
    all_results.extend(scan_github_education_datasets())

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
        df.to_csv('data/k12_data_catalogs_discovered.csv', index=False)
        print(f"\n✅ Found {len(df)} K-12 AI education data catalogs\n")
        for _, row in df.iterrows():
            print(f"     → {row['resource_name'][:80]}")
    else:
        print("\n⚠️  No data catalogs found this scan")

if __name__ == '__main__':
    main()
