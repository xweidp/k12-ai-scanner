#!/usr/bin/env python3
"""
Weekly K-12 AI Inventory Update Script

Scans GitHub and Hugging Face for new K-12 AI datasets/benchmarks/models
and adds them to the existing v18 inventory with discovery dates.

Runs every Monday via GitHub Actions.
"""

import json
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path
import hashlib

# Color codes for terminal output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

def load_base_inventory():
    """Load the v18 base inventory."""
    try:
        df = pd.read_excel('data/k12_inventory_v18_base.xlsx')
        print(f"{GREEN}✓ Loaded base inventory: {len(df)} records{RESET}")
        return df
    except Exception as e:
        print(f"{RED}✗ Error loading base inventory: {e}{RESET}")
        return pd.DataFrame()

def load_scanned_resources():
    """Load newly scanned resources from data/resources.json"""
    try:
        with open('data/resources.json') as f:
            data = json.load(f)
        resources = data.get('resources', [])
        print(f"{GREEN}✓ Loaded {len(resources)} scanned resources{RESET}")
        return resources
    except Exception as e:
        print(f"{RED}✗ Error loading scanned resources: {e}{RESET}")
        return []

def generate_record_id(url):
    """Generate a record ID from URL hash."""
    hash_obj = hashlib.md5(url.encode())
    return f"new_{hash_obj.hexdigest()[:12]}"

def is_already_in_inventory(new_url, existing_urls):
    """Check if URL already exists in inventory (with variants)."""
    for existing_url in existing_urls:
        # Normalize URLs (remove trailing slashes, http/https)
        new_normalized = new_url.lower().rstrip('/').replace('https://', '').replace('http://', '')
        existing_normalized = str(existing_url).lower().rstrip('/').replace('https://', '').replace('http://', '')

        if new_normalized == existing_normalized or existing_url in new_url or new_url in str(existing_url):
            return True
    return False

def find_new_resources(base_inventory, scanned_resources):
    """Identify resources not yet in base inventory."""
    existing_urls = set(base_inventory['url'].tolist()) if 'url' in base_inventory.columns else set()

    new_records = []
    duplicates = []

    for resource in scanned_resources:
        url = resource.get('url', '')
        title = resource.get('title', '')

        if not url:
            continue

        if is_already_in_inventory(url, existing_urls):
            duplicates.append(title[:50])
            continue

        # Create new record matching v18 structure
        new_record = {
            'record_id': generate_record_id(url),
            'resource_name': title,
            'author_name': resource.get('source', ''),
            'url': url,
            'resource_subtype': resource.get('resourceType', 'Dataset'),
            'final_readiness_index_tier': 'Not Reviewed: newly discovered',
            'relevance_status': 'Needs review',
            'subject_area': ', '.join(resource.get('subjects', [])) or 'General',
            'discovery_date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
            'discovery_source': resource.get('source', 'Scanner'),
            'notes': resource.get('description', ''),
            'fit_score': resource.get('fit', 0)
        }
        new_records.append(new_record)
        existing_urls.add(url)

    print(f"{GREEN}✓ Found {len(new_records)} NEW resources{RESET}")
    if duplicates:
        print(f"{YELLOW}ℹ Skipped {len(duplicates)} duplicates{RESET}")

    return new_records

def create_updated_inventory(base_inventory, new_records):
    """Combine base inventory with new records."""
    if not new_records:
        print(f"{YELLOW}ℹ No new resources to add{RESET}")
        return base_inventory

    new_df = pd.DataFrame(new_records)

    # Add missing columns from base to match structure
    for col in base_inventory.columns:
        if col not in new_df.columns:
            new_df[col] = ''

    # Combine with base
    combined = pd.concat([base_inventory, new_df], ignore_index=True)
    combined = combined.drop_duplicates(subset=['url'], keep='first')

    print(f"{GREEN}✓ Updated inventory: {len(combined)} total records{RESET}")
    return combined

def save_inventory(df, format='both'):
    """Save updated inventory to multiple formats."""
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d_%H%M%S')

    if format in ['xlsx', 'both']:
        xlsx_file = f'data/k12_inventory_updated_{timestamp}.xlsx'
        df.to_excel(xlsx_file, index=False)
        print(f"{GREEN}✓ Saved to {xlsx_file}{RESET}")

    if format in ['csv', 'both']:
        csv_file = f'data/k12_inventory_updated_{timestamp}.csv'
        df.to_csv(csv_file, index=False)
        print(f"{GREEN}✓ Saved to {csv_file}{RESET}")

    # Also save as latest
    df.to_csv('data/k12_inventory_latest.csv', index=False)
    print(f"{GREEN}✓ Saved to data/k12_inventory_latest.csv (latest){RESET}")

def create_summary_report(new_records):
    """Create a summary report of new discoveries."""
    if not new_records:
        return

    summary = {
        'scan_date': datetime.now(timezone.utc).isoformat(),
        'new_resources_count': len(new_records),
        'by_source': {},
        'by_type': {},
        'by_subject': {}
    }

    for rec in new_records:
        # By source
        source = rec.get('discovery_source', 'Unknown')
        summary['by_source'][source] = summary['by_source'].get(source, 0) + 1

        # By type
        rtype = rec.get('resource_subtype', 'Unknown')
        summary['by_type'][rtype] = summary['by_type'].get(rtype, 0) + 1

        # By subject
        subjects = rec.get('subject_area', '').split(', ')
        for subject in subjects:
            if subject:
                summary['by_subject'][subject] = summary['by_subject'].get(subject, 0) + 1

    print(f"\n{GREEN}DISCOVERY SUMMARY{RESET}")
    print(f"New resources: {summary['new_resources_count']}")
    print(f"By source: {summary['by_source']}")
    print(f"By type: {summary['by_type']}")
    print(f"By subject: {dict(list(summary['by_subject'].items())[:5])}...")

    with open('data/discovery_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"{GREEN}✓ Saved summary to data/discovery_summary.json{RESET}")

def main():
    print(f"\n{GREEN}=== K-12 AI Inventory Weekly Update ==={RESET}\n")

    # 1. Load base inventory
    base_inventory = load_base_inventory()
    if base_inventory.empty:
        print(f"{RED}Cannot proceed without base inventory{RESET}")
        return False

    # 2. Load scanned resources
    scanned_resources = load_scanned_resources()
    if not scanned_resources:
        print(f"{YELLOW}No scanned resources found (scanner may need to run first){RESET}")
        return False

    # 3. Find new resources
    new_records = find_new_resources(base_inventory, scanned_resources)

    # 4. Create updated inventory
    updated_inventory = create_updated_inventory(base_inventory, new_records)

    # 5. Save
    save_inventory(updated_inventory, format='csv')

    # 6. Create summary
    create_summary_report(new_records)

    print(f"\n{GREEN}✓ Update complete!{RESET}\n")
    return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
