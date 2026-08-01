"""Monitor NSF announcements for K-12 AI education grant funding"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scan_nsf_announcements():
    """Scrape NSF announcements for education AI grants"""
    results = []

    try:
        # NSF STEM education grants
        url = "https://www.nsf.gov/funding/programs/"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find education/AI related program announcements
        programs = soup.find_all('div', class_=['program', 'announcement', 'funding-opportunity'])

        for program in programs:
            title_elem = program.find('h3') or program.find('h2')
            if not title_elem:
                continue

            title = title_elem.get_text(strip=True)

            # Filter for K-12/education AI programs
            if not any(keyword in title.lower() for keyword in
                      ['k-12', 'education', 'stem', 'ai', 'machine learning', 'data science']):
                continue

            # Get link
            link = program.find('a')
            program_url = link.get('href', '') if link else ''
            if program_url and not program_url.startswith('http'):
                program_url = 'https://www.nsf.gov' + program_url

            # Get description
            desc_elem = program.find('p')
            description = desc_elem.get_text(strip=True) if desc_elem else ''

            # Extract funding info if available
            deadline_elem = program.find(string=lambda text: text and 'deadline' in text.lower())
            deadline = ''
            if deadline_elem:
                deadline = deadline_elem.strip()[:50]

            results.append({
                'resource_name': title,
                'organization': 'National Science Foundation (NSF)',
                'announcement_date': datetime.now().strftime('%Y-%m-%d'),
                'expected_release_date': deadline if deadline else '',
                'status': 'Open for Applications',
                'source_url': program_url,
                'description': description,
                'estimated_size': '',
                'source_type': 'government_grant',
                'preview_available': 'Yes',
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            })

    except Exception as e:
        print(f"NSF error: {e}")
        return []

    return results
