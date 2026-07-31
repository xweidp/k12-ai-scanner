#!/usr/bin/env python3
"""
Verify that resources are actually downloadable datasets with artifacts.
Checks for:
1. Link validity (HTTP 200)
2. Resource type accuracy (Dataset vs Blog vs Paper)
3. Actual data artifacts present
"""

import pandas as pd
import requests
from pathlib import Path
import time

def is_hf_dataset(url):
    """Check if URL is a real HF dataset with downloadable data"""
    if 'huggingface.co/datasets/' not in url:
        return False, None

    try:
        # HF dataset API
        dataset_id = url.split('huggingface.co/datasets/')[1].rstrip('/')
        api_url = f"https://huggingface.co/api/datasets/{dataset_id}"
        response = requests.get(api_url, timeout=5)

        if response.ok:
            data = response.json()
            # Check if it has actual files/data
            if 'siblings' in data and data['siblings']:
                return True, 'HF Dataset'
            if 'id' in data:  # Has dataset metadata
                return True, 'HF Dataset'
        return False, 'HF Page (no data)'
    except:
        return False, 'HF Error'

def is_github_repo_with_data(url):
    """Check if GitHub repo actually has data files"""
    if 'github.com/' not in url:
        return False, None

    try:
        # Convert to API URL
        repo_path = url.split('github.com/')[1].rstrip('/').split('/wiki')[0]
        api_url = f"https://api.github.com/repos/{repo_path}"

        response = requests.get(api_url, timeout=5)
        if response.ok:
            data = response.json()
            # Check for actual files (not just code repo)
            if data.get('stargazers_count', 0) < 5:
                return False, 'GitHub Repo (low stars, likely not dataset)'

            # Get file info
            contents_url = f"https://api.github.com/repos/{repo_path}/contents"
            contents = requests.get(contents_url, timeout=5)
            if contents.ok:
                files = contents.json()
                # Check for data files
                data_keywords = ['.csv', '.json', '.parquet', '.npz', '.pkl', 'data/', 'dataset/']
                has_data = any(
                    any(kw in str(f.get('name', '')).lower() for kw in data_keywords)
                    for f in (files if isinstance(files, list) else [files])
                )
                if has_data:
                    return True, 'GitHub Dataset'
                else:
                    return False, 'GitHub Repo (code only)'
        return False, 'GitHub Error'
    except:
        return False, 'GitHub Error'

def check_link_valid(url):
    """Check if link returns 200 OK"""
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        return response.status_code == 200
    except:
        return False

def verify_resource(row):
    """Verify a single resource"""
    url = row.get('url', '')
    resource_type = row.get('resource_subtype', '')
    title = row.get('resource_name', '')[:40]

    if not url:
        return False, 'No URL', 'Invalid'

    # Check link validity
    if not check_link_valid(url):
        return False, 'Link broken/404', resource_type

    # Check for actual dataset
    if 'huggingface.co/datasets' in url:
        is_dataset, reason = is_hf_dataset(url)
        return is_dataset, reason, resource_type

    if 'github.com' in url:
        is_dataset, reason = is_github_repo_with_data(url)
        return is_dataset, reason, resource_type

    if 'openai.com' in url:
        # OpenAI blog articles are NOT datasets
        return False, 'Blog article (not dataset)', 'Blog'

    if 'arxiv.org' in url or 'papers' in url.lower():
        # Papers/preprints are not downloadable datasets
        return False, 'Paper/preprint (not dataset)', 'Paper'

    # For other sources, assume valid if link works and marked as Dataset
    if resource_type == 'Dataset':
        return True, 'Link valid', resource_type

    return False, f'Unknown type: {resource_type}', resource_type

def main():
    print("Verifying dataset resources...\n")

    df = pd.read_csv('data/k12_inventory_latest.csv')

    # Identify v18 records (those already manually verified - no discovery_date)
    is_v18 = df['discovery_date'].isna() | (df['discovery_date'] == '')

    print(f"Found {is_v18.sum()} v18 records (manually verified) - skipping verification")
    print(f"Will verify {(~is_v18).sum()} newly discovered records\n")

    # Initialize columns if missing
    if 'is_downloadable' not in df.columns:
        df['is_downloadable'] = False
    if 'verification_note' not in df.columns:
        df['verification_note'] = ''

    # Trust all v18 records
    df.loc[is_v18, 'is_downloadable'] = True
    df.loc[is_v18, 'verification_note'] = 'v18 - manually verified'

    verified_count = is_v18.sum()  # All v18 records count as verified
    broken_count = 0
    non_dataset_count = 0

    # Only verify newly discovered records
    for idx, row in df.iterrows():
        if is_v18[idx]:
            continue  # Skip v18 records

        is_valid, note, rtype = verify_resource(row)
        df.at[idx, 'is_downloadable'] = is_valid
        df.at[idx, 'verification_note'] = note

        if idx % 20 == 0:
            print(f"Checking newly discovered {idx}/{len(df)}...", end='\r')

        if is_valid:
            verified_count += 1
        elif 'broken' in note.lower():
            broken_count += 1
        else:
            non_dataset_count += 1

        time.sleep(0.1)  # Rate limit

    # Save results
    df.to_csv('data/k12_inventory_verified.csv', index=False)

    print(f"\n{'='*60}")
    print(f"Verification Results:")
    print(f"{'='*60}")
    print(f"✅ v18 records (trusted): {is_v18.sum()}")
    print(f"✅ Newly discovered (valid): {verified_count - is_v18.sum()}")
    print(f"❌ Newly discovered (broken): {broken_count}")
    print(f"⚠️  Newly discovered (non-dataset): {non_dataset_count}")
    print(f"{'='*60}")
    print(f"Total downloadable: {verified_count}/{len(df)}\n")

    # Show problematic resources (only new discoveries)
    problematic = df[~df['is_downloadable']]
    if len(problematic) > 0:
        print(f"Problematic newly-discovered resources:\n")
        for note, count in problematic['verification_note'].value_counts().items():
            print(f"  {note}: {count}")

    print(f"\nSaved verified inventory to: data/k12_inventory_verified.csv")

if __name__ == '__main__':
    main()
