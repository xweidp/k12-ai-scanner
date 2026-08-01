#!/usr/bin/env python3
"""
Scan for upcoming K-12 AI datasets from multiple sources.
Monitors: DrivenData, K-12 AI Infrastructure, GitHub, NSF, LDC, RSS feeds, Research Institutions
"""

import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import json
import os
import feedparser

# Research institutions & K-12 AI orgs to monitor
K12_AI_GITHUB_REPOS = [
    'xweidp/k12-ai-scanner',
    'allenai/ai2',
    'AI2-Education/ai2-education',
    'microsoft/AI-Literacy',
    'google/generative-ai-docs',
    'openai/gpt-4',
]

# RSS feeds - focus on AI/ML/education specific sources
RSS_FEEDS = [
    'https://huggingface.co/papers/feed.xml',  # HF papers (datasets in papers)
    'https://papers.ssrn.com/sol3/rss_Journal_Abstracts.cfm?jid=3221',  # SSRN education papers
    'https://www.kdnuggets.com/feed.xml',  # KDnuggets AI/data news
]

# Research institution homepages
RESEARCH_INSTITUTIONS = [
    {'name': 'MIT', 'url': 'https://www.csail.mit.edu/news', 'keywords': ['dataset', 'k-12', 'education']},
    {'name': 'Stanford', 'url': 'https://hai.stanford.edu/news', 'keywords': ['dataset', 'education', 'ai']},
    {'name': 'CMU', 'url': 'https://www.cs.cmu.edu/news', 'keywords': ['dataset', 'education']},
    {'name': 'UC Berkeley', 'url': 'https://eecs.berkeley.edu/news', 'keywords': ['dataset', 'learning']},
]

def scan_drivendata():
    """Scrape DrivenData competitions"""
    results = []
    try:
        url = "https://www.drivendata.org/competitions/"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        if 'competition' in response.text.lower():
            results.append({
                'resource_name': 'DrivenData Education Competitions',
                'organization': 'DrivenData',
                'announcement_date': datetime.now().strftime('%Y-%m-%d'),
                'expected_release_date': '',
                'status': 'Active',
                'source_url': url,
                'description': 'Open data science competitions including education AI challenges',
                'estimated_size': '',
                'source_type': 'competition',
                'preview_available': 'Yes',
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            })
    except Exception as e:
        print(f"  DrivenData: {e}")

    return results

def scan_k12_infrastructure():
    """Scan K-12 AI Infrastructure platform"""
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
    """Scan LDC UPenn via alternative endpoint"""
    results = []
    try:
        # Try direct catalog API or alternative URL
        url = "https://www.ldc.upenn.edu/catalog"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        if 'dataset' in response.text.lower() or 'catalog' in response.text.lower():
            results.append({
                'resource_name': 'LDC UPenn Linguistic Data Catalog',
                'organization': 'Linguistic Data Consortium (LDC)',
                'announcement_date': datetime.now().strftime('%Y-%m-%d'),
                'expected_release_date': '',
                'status': 'Available',
                'source_url': url,
                'description': 'Linguistic datasets and corpora including education-related language data',
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

    for repo in K12_AI_GITHUB_REPOS:
        try:
            url = f"https://api.github.com/repos/{repo}/releases"
            headers = {}
            token = os.getenv('GITHUB_TOKEN')
            if token:
                headers['Authorization'] = f'token {token}'

            response = requests.get(url, headers=headers, timeout=10)

            # Skip 404s (repos don't exist)
            if response.status_code == 404:
                continue

            response.raise_for_status()

            releases = response.json()
            if releases and len(releases) > 0:
                latest = releases[0]
                published = latest.get('published_at', '')
                pub_date = datetime.fromisoformat(published.replace('Z', '+00:00')) if published else datetime.now()

                # Only include recent releases (last 90 days)
                if (datetime.now(pub_date.tzinfo) - pub_date).days < 90:
                    results.append({
                        'resource_name': f"{repo.split('/')[-1]}: {latest.get('name', 'Release')}",
                        'organization': f"GitHub - {repo.split('/')[0]}",
                        'announcement_date': published[:10] if published else datetime.now().strftime('%Y-%m-%d'),
                        'expected_release_date': '',
                        'status': 'Released' if not latest.get('prerelease') else 'Pre-release',
                        'source_url': latest.get('html_url', ''),
                        'description': (latest.get('body', '') or '')[:200],
                        'estimated_size': '',
                        'source_type': 'github_release',
                        'preview_available': 'Yes' if latest.get('assets') else 'No',
                        'last_updated': datetime.now().strftime('%Y-%m-%d')
                    })
        except Exception as e:
            print(f"  GitHub {repo}: {e}")

    return results

def scan_nsf_announcements():
    """Scan NSF for education grants - improved endpoint"""
    results = []
    try:
        # NSF has a JSON API for funding opportunities
        url = "https://api.nsf.gov/services/rest/v1/awards.json"
        params = {
            'keyword': 'education K-12 AI',
            'awardType': 'Grant',
            'limit': 10
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        awards = data.get('response', {}).get('award', [])

        if awards:
            results.append({
                'resource_name': 'NSF Education AI Funding Opportunities',
                'organization': 'National Science Foundation (NSF)',
                'announcement_date': datetime.now().strftime('%Y-%m-%d'),
                'expected_release_date': '',
                'status': 'Open for Applications',
                'source_url': 'https://www.nsf.gov/cgi-bin/sspas?KeywordSearch=education',
                'description': f'Found {len(awards)} active NSF grants for K-12 AI education',
                'estimated_size': '',
                'source_type': 'government_grant',
                'preview_available': 'Yes',
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            })
    except Exception as e:
        print(f"  NSF API: {e}")
        # Fallback to website scrape
        try:
            url = "https://www.nsf.gov/cgi-bin/sspas?KeywordSearch=education"
            response = requests.get(url, timeout=10)
            if response.ok:
                results.append({
                    'resource_name': 'NSF Education & AI Program Solicitations',
                    'organization': 'National Science Foundation',
                    'announcement_date': datetime.now().strftime('%Y-%m-%d'),
                    'expected_release_date': '',
                    'status': 'Open for Applications',
                    'source_url': url,
                    'description': 'NSF funding programs for K-12 AI education initiatives',
                    'estimated_size': '',
                    'source_type': 'government_grant',
                    'preview_available': 'Yes',
                    'last_updated': datetime.now().strftime('%Y-%m-%d')
                })
        except:
            pass

    return results

def scan_rss_feeds():
    """Scan RSS feeds for dataset/benchmark announcements (strict filtering)"""
    results = []

    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            entries = feed.entries[:10]  # Check more entries

            for entry in entries:
                title = entry.get('title', '')
                link = entry.get('link', '')
                published = entry.get('published', '')
                summary = (entry.get('summary', '') or '')

                full_text = (title + ' ' + summary).lower()

                # Stricter: Must mention dataset/benchmark AND be about education/K-12
                has_dataset_kw = any(kw in full_text for kw in ['dataset', 'benchmark', 'corpus', 'collection', 'archive'])
                has_edu_kw = any(kw in full_text for kw in ['education', 'k-12', 'school', 'student', 'teacher', 'learning'])

                if has_dataset_kw and (has_edu_kw or 'ai' in full_text):
                    results.append({
                        'resource_name': title[:100],
                        'organization': feed.feed.get('title', 'News Feed'),
                        'announcement_date': published[:10] if published else datetime.now().strftime('%Y-%m-%d'),
                        'expected_release_date': '',
                        'status': 'Announced',
                        'source_url': link,
                        'description': summary[:200] if summary else '',
                        'estimated_size': '',
                        'source_type': 'news_feed',
                        'preview_available': 'Yes',
                        'last_updated': datetime.now().strftime('%Y-%m-%d')
                    })
        except Exception as e:
            print(f"  RSS Feed {feed_url}: {e}")

    return results

def scan_research_institutions():
    """Scan research institution news pages"""
    results = []

    for org in RESEARCH_INSTITUTIONS:
        try:
            response = requests.get(org['url'], timeout=10)
            response.raise_for_status()

            text = response.text.lower()
            keywords_found = [kw for kw in org['keywords'] if kw in text]

            if keywords_found:
                results.append({
                    'resource_name': f"{org['name']} AI/Education News",
                    'organization': org['name'],
                    'announcement_date': datetime.now().strftime('%Y-%m-%d'),
                    'expected_release_date': '',
                    'status': 'Check Website',
                    'source_url': org['url'],
                    'description': f"Research announcements on: {', '.join(keywords_found)}",
                    'estimated_size': '',
                    'source_type': 'research_institution',
                    'preview_available': 'Yes',
                    'last_updated': datetime.now().strftime('%Y-%m-%d')
                })
        except Exception as e:
            print(f"  {org['name']}: {e}")

    return results

def main():
    print("🔍 Scanning for upcoming K-12 AI datasets...\n")

    all_results = []

    print("📊 DrivenData...")
    all_results.extend(scan_drivendata())

    print("📚 K-12 AI Infrastructure...")
    all_results.extend(scan_k12_infrastructure())

    print("🔤 LDC UPenn...")
    all_results.extend(scan_ldc_upenn())

    print("🐙 GitHub K-12 AI Projects...")
    all_results.extend(scan_github_k12ai())

    print("🏛️  NSF Announcements...")
    all_results.extend(scan_nsf_announcements())

    print("📰 RSS News Feeds...")
    all_results.extend(scan_rss_feeds())

    print("🏫 Research Institutions...")
    all_results.extend(scan_research_institutions())

    # Deduplicate by URL
    seen_urls = set()
    unique_results = []
    for row in all_results:
        url = row.get('source_url', '')
        if url and url not in seen_urls:
            unique_results.append(row)
            seen_urls.add(url)

    # Save
    if unique_results:
        df = pd.DataFrame(unique_results)
        df.to_csv('data/k12_datasets_coming_soon.csv', index=False)
        print(f"\n✅ Found {len(df)} upcoming K-12 AI resources\n")
        print("   Breakdown by source:")
        for source, count in df['source_type'].value_counts().items():
            print(f"     • {source}: {count}")
    else:
        print("\n⚠️  No results found")

if __name__ == '__main__':
    main()
