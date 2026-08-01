"""Scan K-12 AI Infrastructure platform for new datasets"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scan_k12_infrastructure():
    """Scrape K-12 AI Infrastructure platform for datasets"""
    results = []

    try:
        url = "https://platform.k12-ai-infrastructure.org/datasets/"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all dataset entries (adjust selectors based on actual HTML)
        datasets = soup.find_all('div', class_=['dataset-item', 'card', 'resource'])

        for dataset in datasets:
            # Try multiple selectors for title
            title_elem = (dataset.find('h3') or dataset.find('h2') or
                         dataset.find(class_=['title', 'name']))
            if not title_elem:
                continue

            title = title_elem.get_text(strip=True)

            # Get link
            link = dataset.find('a')
            dataset_url = link.get('href', '') if link else ''
            if not dataset_url.startswith('http'):
                dataset_url = 'https://platform.k12-ai-infrastructure.org' + dataset_url

            # Get description
            desc_elem = dataset.find('p') or dataset.find(class_='description')
            description = desc_elem.get_text(strip=True) if desc_elem else ''

            # Check for "new" or "coming soon" indicators
            status = 'Available'
            if any(word in description.lower() or title.lower()
                   for word in ['coming', 'soon', 'beta', 'preview', 'new']):
                status = 'Coming Soon'

            results.append({
                'resource_name': title,
                'organization': 'K-12 AI Infrastructure',
                'announcement_date': datetime.now().strftime('%Y-%m-%d'),
                'expected_release_date': '',
                'status': status,
                'source_url': dataset_url,
                'description': description,
                'estimated_size': '',
                'source_type': 'platform',
                'preview_available': 'Yes' if status == 'Available' else 'No',
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            })

    except Exception as e:
        print(f"K-12 Infrastructure error: {e}")
        return []

    return results
