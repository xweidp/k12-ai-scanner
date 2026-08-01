"""Scan DrivenData for upcoming K-12 AI competitions and datasets"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scan_drivendata():
    """Scrape DrivenData competitions and extract K-12 AI relevant ones"""
    results = []

    try:
        url = "https://www.drivendata.org/competitions/"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all competition cards
        competitions = soup.find_all('div', class_='competition-card')

        for comp in competitions:
            title_elem = comp.find('h3') or comp.find('a')
            if not title_elem:
                continue

            title = title_elem.get_text(strip=True)

            # Filter for K-12/education related
            if any(keyword in title.lower() for keyword in
                   ['k-12', 'k12', 'education', 'student', 'teacher', 'learning', 'school']):

                comp_url = comp.find('a')
                if comp_url:
                    comp_url = comp_url.get('href', '')
                    if not comp_url.startswith('http'):
                        comp_url = 'https://www.drivendata.org' + comp_url

                # Try to extract description and status
                desc_elem = comp.find('p')
                description = desc_elem.get_text(strip=True) if desc_elem else ''

                results.append({
                    'resource_name': title,
                    'organization': 'DrivenData',
                    'announcement_date': datetime.now().strftime('%Y-%m-%d'),
                    'expected_release_date': '',
                    'status': 'Active Competition',
                    'source_url': comp_url,
                    'description': description,
                    'estimated_size': '',
                    'source_type': 'competition',
                    'preview_available': 'Yes',
                    'last_updated': datetime.now().strftime('%Y-%m-%d')
                })

    except Exception as e:
        print(f"DrivenData error: {e}")
        return []

    return results
