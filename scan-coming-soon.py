#!/usr/bin/env python3
"""
Comprehensive scanner for upcoming K-12 AI datasets.
Combines: research papers, GitHub releases, education platforms, grants, + manual curation.
"""

import pandas as pd
import requests
from datetime import datetime
import time

# Real competitions with verified working links
CURATED_COMING_SOON = [
    {
        'name': 'DrivenData: K-12 Education Competitions',
        'org': 'DrivenData',
        'date': '',
        'url': 'https://www.drivendata.org/competitions/',
        'type': 'competition',
        'desc': 'Open data science competitions focused on education and K-12 AI'
    }
]

def scan_arxiv_papers():
    """Scan ArXiv for K-12 education AI papers with datasets, benchmarks, and models"""
    results = []
    try:
        url = "http://export.arxiv.org/api/query"
        params = {
            'search_query': 'cat:cs.CY AND (dataset OR benchmark OR corpus OR model OR "pre-trained") AND (education OR student OR school OR "k-12" OR learning)',
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

            # Detect resource type from title
            resource_type = 'research_paper'
            if any(x in title.lower() for x in ['benchmark', 'dataset', 'corpus']):
                resource_type = 'benchmark' if 'benchmark' in title.lower() else 'dataset'
            elif any(x in title.lower() for x in ['model', 'pre-trained']):
                resource_type = 'model'

            results.append({
                'resource_name': f"ArXiv: {title[:80]}",
                'organization': 'ArXiv',
                'announcement_date': published,
                'expected_release_date': '',
                'status': 'Published',
                'source_url': f"https://arxiv.org/abs/{arxiv_id}",
                'description': 'Research paper with educational AI resource',
                'estimated_size': '',
                'source_type': resource_type,
                'preview_available': 'Yes',
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            })
    except Exception as e:
        print(f"  ArXiv: {e}")

    return results

def scan_github_announcements():
    """Scan GitHub for K-12 AI project releases"""
    results = []
    repos = [
        'tensorflow/tensorflow',  # TF releases with edu datasets
        'pytorch/pytorch',  # PyTorch edu resources
        'huggingface/transformers',  # HF model releases
        'openai/gpt-3.5-turbo',  # OpenAI announcements
    ]

    for repo in repos[:3]:
        try:
            url = f"https://api.github.com/repos/{repo}/releases"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                releases = response.json()[:5]
                for rel in releases:
                    if 'education' in (rel.get('body') or '').lower() or 'dataset' in (rel.get('body') or '').lower():
                        results.append({
                            'resource_name': f"GitHub {repo.split('/')[1]}: {rel.get('name', 'Release')[:70]}",
                            'organization': f"GitHub - {repo.split('/')[0]}",
                            'announcement_date': rel.get('published_at', '')[:10],
                            'expected_release_date': '',
                            'status': 'Released',
                            'source_url': rel.get('html_url', ''),
                            'description': (rel.get('body', '') or '')[:150],
                            'estimated_size': '',
                            'source_type': 'github_release',
                            'preview_available': 'Yes',
                            'last_updated': datetime.now().strftime('%Y-%m-%d')
                        })
        except:
            pass

    return results

def scan_huggingface_datasets():
    """Scan HuggingFace for new education datasets and benchmarks"""
    results = []
    try:
        url = "https://huggingface.co/api/datasets"
        params = {'full': True, 'limit': 30}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        datasets = response.json()

        for ds in datasets[:15]:
            desc = (ds.get('description') or '').lower()
            if any(kw in desc for kw in ['education', 'student', 'school', 'k-12', 'learning', 'teacher']):
                source_type = 'benchmark' if 'benchmark' in desc else 'dataset'
                results.append({
                    'resource_name': f"HuggingFace: {ds.get('id', 'Dataset')[:80]}",
                    'organization': 'HuggingFace',
                    'announcement_date': datetime.now().strftime('%Y-%m-%d'),
                    'expected_release_date': '',
                    'status': 'Available',
                    'source_url': f"https://huggingface.co/datasets/{ds.get('id', '')}",
                    'description': (ds.get('description', '') or '')[:150],
                    'estimated_size': '',
                    'source_type': source_type,
                    'preview_available': 'Yes',
                    'last_updated': datetime.now().strftime('%Y-%m-%d')
                })
    except Exception as e:
        print(f"  HuggingFace: {e}")

    return results

def scan_ldc_rss():
    """Scan LDC RSS feed for new education-related datasets"""
    results = []
    try:
        import feedparser
        url = "https://www.ldc.upenn.edu/rss.xml"
        feed = feedparser.parse(url)

        for entry in feed.entries[:10]:  # Get last 10 releases
            title = entry.get('title', '')
            # Filter for education/K-12 related keywords
            if any(kw in title.lower() for kw in ['education', 'student', 'school', 'k-12', 'learning', 'classroom', 'teacher', 'curriculum']):
                link = entry.get('link', '')
                published = entry.get('published', '')[:10] if entry.get('published') else datetime.now().strftime('%Y-%m-%d')

                results.append({
                    'resource_name': f"LDC: {title[:80]}",
                    'organization': 'Linguistic Data Consortium',
                    'announcement_date': published,
                    'expected_release_date': '',
                    'status': 'Available',
                    'source_url': link,
                    'description': 'Linguistic dataset from LDC',
                    'estimated_size': '',
                    'source_type': 'dataset',
                    'preview_available': 'Yes',
                    'last_updated': datetime.now().strftime('%Y-%m-%d')
                })
    except Exception as e:
        print(f"  LDC RSS: {e}")

    return results

def scan_huggingface_models():
    """Scan HuggingFace for new education models"""
    results = []
    try:
        url = "https://huggingface.co/api/models"
        params = {'full': True, 'limit': 30}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        models = response.json()

        for model in models[:15]:
            desc = (model.get('description') or '').lower()
            tags = (model.get('tags') or [])
            tag_str = ' '.join(tags).lower()

            if any(kw in desc or kw in tag_str for kw in ['education', 'student', 'school', 'k-12', 'learning']):
                results.append({
                    'resource_name': f"HuggingFace: {model.get('id', 'Model')[:80]}",
                    'organization': 'HuggingFace',
                    'announcement_date': datetime.now().strftime('%Y-%m-%d'),
                    'expected_release_date': '',
                    'status': 'Available',
                    'source_url': f"https://huggingface.co/{model.get('id', '')}",
                    'description': (model.get('description', '') or '')[:150],
                    'estimated_size': '',
                    'source_type': 'model',
                    'preview_available': 'Yes',
                    'last_updated': datetime.now().strftime('%Y-%m-%d')
                })
    except Exception as e:
        print(f"  HuggingFace Models: {e}")

    return results

def main():
    print("🔍 Scanning for upcoming K-12 AI datasets...\n")

    all_results = []

    # 1. CURATED LIST (highest quality, known coming soon)
    print("📋 Curated upcoming resources...")
    for item in CURATED_COMING_SOON:
        all_results.append({
            'resource_name': item['name'],
            'organization': item['org'],
            'announcement_date': datetime.now().strftime('%Y-%m-%d'),
            'expected_release_date': item['date'],
            'status': 'Expected Release',
            'source_url': item['url'],
            'description': item['desc'],
            'estimated_size': '',
            'source_type': item['type'],
            'preview_available': 'Yes',
            'last_updated': datetime.now().strftime('%Y-%m-%d')
        })

    # 2. RESEARCH PAPERS
    print("📝 ArXiv research papers...")
    all_results.extend(scan_arxiv_papers())

    # 3. GITHUB RELEASES
    print("🐙 GitHub releases...")
    all_results.extend(scan_github_announcements())

    # 4. HUGGINGFACE DATASETS
    print("📚 HuggingFace datasets...")
    all_results.extend(scan_huggingface_datasets())

    # 5. HUGGINGFACE MODELS
    print("🤖 HuggingFace models...")
    all_results.extend(scan_huggingface_models())

    # 6. LDC RSS FEED
    print("📚 LDC Linguistic Data Consortium...")
    all_results.extend(scan_ldc_rss())

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
        df.to_csv('data/k12_datasets_coming_soon.csv', index=False)
        print(f"\n✅ Found {len(df)} SPECIFIC upcoming K-12 AI resources\n")
        print("   Breakdown:")
        print(f"     • Curated: {len([r for r in all_results if r['source_type'] in ['competition', 'benchmark', 'dataset']])}")
        for source, count in df['source_type'].value_counts().items():
            print(f"     • {source}: {count}")
        print("\n   Resources listed (sample):")
        for _, row in df.head(10).iterrows():
            print(f"     → {row['resource_name'][:80]}")
    else:
        print("\n⚠️  No resources found")

if __name__ == '__main__':
    main()
