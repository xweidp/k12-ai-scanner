"""Monitor GitHub for K-12 AI project releases and new datasets"""

import requests
from datetime import datetime, timedelta
import os

def scan_github_k12ai():
    """Monitor GitHub repos for K-12 AI dataset releases"""
    results = []

    # K-12 AI related repos to monitor
    repos = [
        'xweidp/k12-ai-scanner',
        'allenai/ai2-education',
        'google/education-ai',
        'microsoft/k12-education-ai',
        # Add more as needed
    ]

    github_token = os.getenv('GITHUB_TOKEN')
    headers = {}
    if github_token:
        headers['Authorization'] = f'token {github_token}'

    for repo in repos:
        try:
            # Check releases
            url = f"https://api.github.com/repos/{repo}/releases"
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            releases = response.json()

            # Get releases from last 30 days
            cutoff = datetime.now() - timedelta(days=30)

            for release in releases[:10]:  # Check recent releases
                published = release.get('published_at', '')
                if published:
                    try:
                        pub_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
                        if pub_date < cutoff:
                            continue
                    except:
                        pass

                title = release.get('name', release.get('tag_name', 'Release'))
                body = release.get('body', '')

                # Filter for dataset-related releases
                if any(keyword in (title + body).lower() for keyword in
                       ['dataset', 'data', 'benchmark', 'k-12', 'education']):

                    results.append({
                        'resource_name': f"{repo.split('/')[1]}: {title}",
                        'organization': f"GitHub - {repo.split('/')[0]}",
                        'announcement_date': published[:10] if published else datetime.now().strftime('%Y-%m-%d'),
                        'expected_release_date': '',
                        'status': 'Released' if not release.get('prerelease') else 'Pre-release',
                        'source_url': release.get('html_url', ''),
                        'description': body[:200] if body else '',
                        'estimated_size': '',
                        'source_type': 'github_release',
                        'preview_available': 'Yes' if release.get('assets') else 'No',
                        'last_updated': datetime.now().strftime('%Y-%m-%d')
                    })

        except Exception as e:
            print(f"GitHub {repo} error: {e}")
            continue

    return results
