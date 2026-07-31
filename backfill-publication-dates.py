#!/usr/bin/env python3
"""
Backfill publication_date field by querying Hugging Face and GitHub APIs
"""

import pandas as pd
import requests
from datetime import datetime
import os
import time

def get_hf_dataset_date(dataset_id):
    """Get creation date of HF dataset"""
    try:
        url = f"https://huggingface.co/api/datasets/{dataset_id}"
        response = requests.get(url, timeout=5)
        if response.ok:
            data = response.json()
            # Try to get created_at or last_modified
            if 'createdAt' in data:
                date_str = data['createdAt'].split('T')[0]
                return date_str
            if 'last_modified' in data:
                date_str = data['last_modified'].split('T')[0]
                return date_str
    except Exception as e:
        pass
    return None

def get_github_repo_date(owner_repo):
    """Get creation date of GitHub repo"""
    try:
        headers = {}
        token = os.getenv('GITHUB_TOKEN')
        if token:
            headers['Authorization'] = f'token {token}'

        url = f"https://api.github.com/repos/{owner_repo}"
        response = requests.get(url, headers=headers, timeout=5)
        if response.ok:
            data = response.json()
            if 'created_at' in data:
                date_str = data['created_at'].split('T')[0]
                return date_str
    except Exception as e:
        pass
    return None

def extract_hf_id(url):
    """Extract dataset ID from HF URL"""
    if 'huggingface.co/datasets/' in url:
        parts = url.split('huggingface.co/datasets/')
        if len(parts) > 1:
            dataset_id = parts[1].rstrip('/')
            return dataset_id
    return None

def extract_github_repo(url):
    """Extract owner/repo from GitHub URL"""
    if 'github.com/' in url:
        parts = url.split('github.com/')
        if len(parts) > 1:
            repo_path = parts[1].rstrip('/').split('/wiki')[0]  # Remove /wiki if present
            # repo_path should be owner/repo or owner/repo/...
            segments = repo_path.split('/')
            if len(segments) >= 2:
                return f"{segments[0]}/{segments[1]}"
    return None

def main():
    print("Backfilling publication_date from APIs...\n")

    df = pd.read_csv('data/k12_inventory_latest.csv')

    if 'publication_date' not in df.columns:
        print("ERROR: publication_date column not found. Run add-publication-date.py first.")
        return

    missing = (df['publication_date'] == '').sum()
    print(f"Records without publication_date: {missing}/{len(df)}")

    count_filled = 0

    for idx, row in df.iterrows():
        if pd.notna(row['publication_date']) and row['publication_date'] != '':
            continue  # Already has date

        url = row.get('url', '')

        # Try Hugging Face
        hf_id = extract_hf_id(url)
        if hf_id:
            date = get_hf_dataset_date(hf_id)
            if date:
                df.at[idx, 'publication_date'] = date
                print(f"  ✓ {row['resource_name'][:50]} → {date} (HF)")
                count_filled += 1
                time.sleep(0.2)  # Rate limit
                continue

        # Try GitHub
        github_repo = extract_github_repo(url)
        if github_repo:
            date = get_github_repo_date(github_repo)
            if date:
                df.at[idx, 'publication_date'] = date
                print(f"  ✓ {row['resource_name'][:50]} → {date} (GitHub)")
                count_filled += 1
                time.sleep(0.2)  # Rate limit
                continue

        # Could add more sources here (arXiv, OpenDataLab, etc.)

    # Save updated inventory
    df.to_csv('data/k12_inventory_latest.csv', index=False)

    print(f"\n✅ Filled {count_filled} publication dates")
    filled_now = (df['publication_date'] != '').sum()
    print(f"Total records with publication_date: {filled_now}/{len(df)}")

if __name__ == '__main__':
    main()
