"""Scan LDC UPenn for education-related linguistic datasets"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scan_ldc_upenn():
    """Scrape LDC UPenn for K-12/education linguistic datasets"""
    results = []

    try:
        # LDC catalog page
        url = "https://www.ldc.upenn.edu/language-resources/data-sets"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all dataset listings
        datasets = soup.find_all('div', class_=['dataset', 'resource', 'listing'])

        for dataset in datasets:
            # Get title
            title_elem = dataset.find('h3') or dataset.find('h2') or dataset.find('a')
            if not title_elem:
                continue

            title = title_elem.get_text(strip=True)

            # Filter for education-related
            if not any(keyword in title.lower() for keyword in
                      ['education', 'student', 'teacher', 'learning', 'school', 'k-12']):
                continue

            # Get URL
            link = dataset.find('a')
            dataset_url = link.get('href', '') if link else ''
            if dataset_url and not dataset_url.startswith('http'):
                dataset_url = 'https://www.ldc.upenn.edu' + dataset_url

            # Get description
            desc_elem = dataset.find('p')
            description = desc_elem.get_text(strip=True) if desc_elem else ''

            results.append({
                'resource_name': title,
                'organization': 'LDC UPenn',
                'announcement_date': datetime.now().strftime('%Y-%m-%d'),
                'expected_release_date': '',
                'status': 'Available',
                'source_url': dataset_url,
                'description': description,
                'estimated_size': '',
                'source_type': 'linguistic_data',
                'preview_available': 'Yes',
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            })

    except Exception as e:
        print(f"LDC UPenn error: {e}")
        return []

    return results
