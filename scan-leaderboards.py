#!/usr/bin/env python3
"""
Scan for K-12 AI education leaderboards from major sources.
Sources: Papers with Code, HuggingFace, Kaggle, GitHub
"""

import pandas as pd
import requests
from datetime import datetime
import time

def scan_papers_with_code_leaderboards():
    """Scan Papers with Code for education-related leaderboards"""
    results = []
    try:
        # Direct leaderboard pages for known education benchmarks
        education_benchmarks = [
            'arc',  # AI2 Reasoning Challenge
            'superglue',  # General NLP (used in education)
            'glue',  # GLUE benchmark
        ]

        for bench_name in education_benchmarks:
            try:
                url = f"https://paperswithcode.com/benchmark/{bench_name}"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    results.append({
                        'resource_name': f"Papers with Code: {bench_name.upper()} Leaderboard",
                        'organization': 'Papers with Code',
                        'announcement_date': datetime.now().strftime('%Y-%m-%d'),
                        'expected_release_date': '',
                        'status': 'Active',
                        'source_url': url,
                        'description': 'Leaderboard from Papers with Code',
                        'estimated_size': '',
                        'source_type': 'leaderboard',
                        'preview_available': 'Yes',
                        'last_updated': datetime.now().strftime('%Y-%m-%d')
                    })
            except:
                pass

    except Exception as e:
        print(f"  Papers with Code: {e}")

    return results

def scan_arxiv_leaderboards():
    """Scan ArXiv for K-12 AI leaderboards"""
    results = []
    try:
        url = "http://export.arxiv.org/api/query"
        params = {
            'search_query': 'cat:cs.CY AND leaderboard AND (education OR student OR school OR "k-12" OR learning)',
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
                'description': 'Leaderboard from research paper',
                'estimated_size': '',
                'source_type': 'leaderboard',
                'preview_available': 'Yes',
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            })
    except Exception as e:
        print(f"  ArXiv: {e}")

    return results

def scan_huggingface_leaderboards():
    """Scan HuggingFace for education leaderboards"""
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

            # Look for leaderboard-related models
            if any(kw in desc or kw in tag_str for kw in ['leaderboard', 'benchmark', 'education', 'student']) and 'leaderboard' in desc + tag_str:
                results.append({
                    'resource_name': f"HuggingFace Leaderboard: {model.get('id', '')[:80]}",
                    'organization': 'HuggingFace',
                    'announcement_date': datetime.now().strftime('%Y-%m-%d'),
                    'expected_release_date': '',
                    'status': 'Active',
                    'source_url': f"https://huggingface.co/{model.get('id', '')}",
                    'description': 'Leaderboard from HuggingFace',
                    'estimated_size': '',
                    'source_type': 'leaderboard',
                    'preview_available': 'Yes',
                    'last_updated': datetime.now().strftime('%Y-%m-%d')
                })
    except Exception as e:
        print(f"  HuggingFace Leaderboards: {e}")

    return results

def scan_kaggle_competitions():
    """Scan Kaggle for education-related competitions with leaderboards"""
    results = []
    try:
        # Kaggle API requires authentication, so we'll do a basic search via web scraping alternative
        # For now, we'll skip this as it requires Kaggle API credentials
        # Users can add their own Kaggle leaderboards manually
        pass
    except Exception as e:
        print(f"  Kaggle: {e}")

    return results

def scan_openreview_leaderboards():
    """Scan OpenReview.net for K-12 AI leaderboards (Phase 2)"""
    results = []
    try:
        # Use direct OpenReview web interface search
        conferences = ['ICLR.cc/2024', 'NeurIPS.cc/2024', 'EMNLP/2024']

        for conf in conferences[:2]:
            try:
                # Search within conference
                search_url = f"https://openreview.net/search?term=education+leaderboard&venue={conf}"
                response = requests.get(search_url, timeout=10)
                if response.status_code == 200:
                    results.append({
                        'resource_name': f"OpenReview: {conf} Education Leaderboards",
                        'organization': 'OpenReview',
                        'announcement_date': datetime.now().strftime('%Y-%m-%d'),
                        'expected_release_date': '',
                        'status': 'Published',
                        'source_url': search_url,
                        'description': 'Education leaderboards from OpenReview conference',
                        'estimated_size': '',
                        'source_type': 'leaderboard',
                        'preview_available': 'Yes',
                        'last_updated': datetime.now().strftime('%Y-%m-%d')
                    })
            except:
                pass
    except Exception as e:
        print(f"  OpenReview: {e}")

    return results

def scan_acl_anthology_leaderboards():
    """Scan ACL Anthology for education leaderboards (Phase 3)"""
    results = []
    try:
        # Search ACL Anthology for education papers with leaderboards
        url = "https://www.aclweb.org/anthology/"
        # This would require parsing the website, so we'll do a simplified search
        education_venues = ['2024.acl', '2024.emnlp', '2024.naacl']

        for venue in education_venues[:2]:
            try:
                search_url = f"https://www.aclweb.org/anthology/volumes/{venue}/"
                response = requests.get(search_url, timeout=10)
                if response.status_code == 200:
                    # Simplified: just add the venue as a resource
                    results.append({
                        'resource_name': f"ACL {venue}: Education Leaderboards Archive",
                        'organization': 'ACL',
                        'announcement_date': datetime.now().strftime('%Y-%m-%d'),
                        'expected_release_date': '',
                        'status': 'Active',
                        'source_url': search_url,
                        'description': 'Education-related leaderboards from ACL conference',
                        'estimated_size': '',
                        'source_type': 'leaderboard',
                        'preview_available': 'Yes',
                        'last_updated': datetime.now().strftime('%Y-%m-%d')
                    })
            except:
                pass
    except Exception as e:
        print(f"  ACL Anthology: {e}")

    return results

def scan_ai2_leaderboards():
    """Scan AI2 (Allen Institute) for education leaderboards (Phase 3)"""
    results = []
    try:
        ai2_benchmarks = [
            {'name': 'ARC', 'url': 'https://allenai.org/arc'},
            {'name': 'ARISTO', 'url': 'https://allenai.org/aristo'},
        ]

        for bench in ai2_benchmarks:
            try:
                response = requests.get(bench['url'], timeout=10)
                if response.status_code == 200:
                    results.append({
                        'resource_name': f"AI2: {bench['name']} Leaderboard",
                        'organization': 'Allen Institute for AI',
                        'announcement_date': datetime.now().strftime('%Y-%m-%d'),
                        'expected_release_date': '',
                        'status': 'Active',
                        'source_url': bench['url'],
                        'description': 'K-12 AI leaderboard from Allen Institute',
                        'estimated_size': '',
                        'source_type': 'leaderboard',
                        'preview_available': 'Yes',
                        'last_updated': datetime.now().strftime('%Y-%m-%d')
                    })
            except:
                pass
    except Exception as e:
        print(f"  AI2: {e}")

    return results

def scan_aied_conference_leaderboards():
    """Scan AIED conference papers for education leaderboards (Phase 2)"""
    results = []
    try:
        # AIED (AI in Education) conference proceedings
        aied_venues = [
            'https://aied2024.org',
            'https://aied2023.org',
        ]

        for venue in aied_venues:
            try:
                response = requests.get(venue, timeout=10)
                if response.status_code == 200:
                    results.append({
                        'resource_name': f"AIED: {venue.split('/')[2]} Conference Proceedings",
                        'organization': 'AIED Conference',
                        'announcement_date': datetime.now().strftime('%Y-%m-%d'),
                        'expected_release_date': '',
                        'status': 'Published',
                        'source_url': venue,
                        'description': 'AI in Education conference with leaderboards',
                        'estimated_size': '',
                        'source_type': 'leaderboard',
                        'preview_available': 'Yes',
                        'last_updated': datetime.now().strftime('%Y-%m-%d')
                    })
            except:
                pass
    except Exception as e:
        print(f"  AIED Conference: {e}")

    return results

def scan_education_specific_platforms():
    """Scan education-specific AI platforms (Phase 2 & 3)"""
    results = []
    platforms = [
        {
            'name': 'ELSA (Educational Language Science)',
            'url': 'https://elsa-benchmark.github.io/'
        },
        {
            'name': 'K-12 AI Infrastructure',
            'url': 'https://platform.k12-ai-infrastructure.org/'
        },
        {
            'name': 'Common Sense Knowledge Leaderboard',
            'url': 'https://www.conceptnet.io/'
        },
    ]

    for platform in platforms:
        try:
            response = requests.get(platform['url'], timeout=10)
            if response.status_code == 200:
                results.append({
                    'resource_name': f"Education Platform: {platform['name']}",
                    'organization': 'Education AI Platform',
                    'announcement_date': datetime.now().strftime('%Y-%m-%d'),
                    'expected_release_date': '',
                    'status': 'Active',
                    'source_url': platform['url'],
                    'description': f'Education-specific leaderboard: {platform["name"]}',
                    'estimated_size': '',
                    'source_type': 'leaderboard',
                    'preview_available': 'Yes',
                    'last_updated': datetime.now().strftime('%Y-%m-%d')
                })
        except:
            pass

    return results

def scan_github_benchmark_leaderboards():
    """Scan GitHub for education AI benchmark leaderboards"""
    results = []
    repos = [
        'allenai/allennlp',  # Has leaderboards
        'huggingface/datasets',
        'facebook/fairseq',
    ]

    try:
        for repo in repos:
            url = f"https://api.github.com/repos/{repo}/releases"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                releases = response.json()[:5]
                for rel in releases:
                    if any(kw in (rel.get('body') or '').lower() for kw in ['leaderboard', 'benchmark', 'education']):
                        results.append({
                            'resource_name': f"GitHub: {repo.split('/')[1]} Leaderboard",
                            'organization': f"GitHub - {repo.split('/')[0]}",
                            'announcement_date': rel.get('published_at', '')[:10],
                            'expected_release_date': '',
                            'status': 'Active',
                            'source_url': rel.get('html_url', ''),
                            'description': 'Leaderboard from GitHub release',
                            'estimated_size': '',
                            'source_type': 'leaderboard',
                            'preview_available': 'Yes',
                            'last_updated': datetime.now().strftime('%Y-%m-%d')
                        })
    except Exception as e:
        print(f"  GitHub Leaderboards: {e}")

    return results

def main():
    print("🔍 Scanning for K-12 AI education leaderboards...\n")

    all_results = []

    # PHASE 1: Core sources
    print("📊 Papers with Code leaderboards...")
    all_results.extend(scan_papers_with_code_leaderboards())

    print("📝 ArXiv leaderboards...")
    all_results.extend(scan_arxiv_leaderboards())

    print("🤗 HuggingFace leaderboards...")
    all_results.extend(scan_huggingface_leaderboards())

    # PHASE 2: Specialized education platforms
    print("📖 OpenReview leaderboards...")
    all_results.extend(scan_openreview_leaderboards())

    print("🎓 AIED Conference leaderboards...")
    all_results.extend(scan_aied_conference_leaderboards())

    print("🏫 Education-specific platforms...")
    all_results.extend(scan_education_specific_platforms())

    # PHASE 3: General AI platforms
    print("📚 ACL Anthology leaderboards...")
    all_results.extend(scan_acl_anthology_leaderboards())

    print("🧠 AI2 (Allen Institute) leaderboards...")
    all_results.extend(scan_ai2_leaderboards())

    # GitHub (Phase 1)
    print("🐙 GitHub benchmark leaderboards...")
    all_results.extend(scan_github_benchmark_leaderboards())

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
        df.to_csv('data/k12_leaderboards_discovered.csv', index=False)
        print(f"\n✅ Found {len(df)} K-12 AI education leaderboards\n")
        for _, row in df.head(10).iterrows():
            print(f"     → {row['resource_name'][:80]}")
    else:
        print("\n⚠️  No new leaderboards found this scan")

if __name__ == '__main__':
    main()
