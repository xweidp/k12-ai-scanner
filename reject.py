#!/usr/bin/env python3
"""
Remove a resource from the inventory AND remember the decision.

Deleting a row from k12_inventory_latest.csv by itself is not durable: the
monthly scan dedupes incoming finds against the URLs currently in the
inventory, so a deleted URL looks brand new on the next run and comes straight
back. This script does both halves - drops the row and appends the URL to
data/rejected_urls.csv, which the workflow treats as permanently excluded.

Usage
  # by URL (exact)
  python3 reject.py --url https://example.org/thing --reason "not K-12"

  # by name (substring, case-insensitive) - previews and asks before deleting
  python3 reject.py --name "SUPERGLUE"

  # see what's currently blocked
  python3 reject.py --list
"""

import argparse
import os
import sys
from datetime import date

import pandas as pd

INVENTORY = 'data/k12_inventory_latest.csv'
REJECTED = 'data/rejected_urls.csv'


def load_rejected():
    if os.path.exists(REJECTED):
        return pd.read_csv(REJECTED)
    return pd.DataFrame(columns=['url', 'resource_name', 'rejected_from',
                                 'rejected_date', 'reason'])


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--url', help='exact URL to remove')
    ap.add_argument('--name', help='substring of resource_name to remove')
    ap.add_argument('--reason', default='Removed during manual review',
                    help='why it was rejected (recorded in the list)')
    ap.add_argument('--list', action='store_true', help='show the rejection list')
    ap.add_argument('--yes', action='store_true', help='skip the confirmation prompt')
    args = ap.parse_args()

    rejected = load_rejected()

    if args.list:
        print(f'{len(rejected)} rejected URLs:\n')
        for _, r in rejected.iterrows():
            print(f"  {str(r['resource_name'])[:60]:60} {r['url']}")
        return

    if not args.url and not args.name:
        ap.error('give --url or --name (or --list)')

    inv = pd.read_csv(INVENTORY)

    if args.url:
        match = inv[inv['url'] == args.url]
    else:
        match = inv[inv['resource_name'].astype(str)
                    .str.contains(args.name, case=False, na=False)]

    if match.empty:
        sys.exit(f'No inventory rows matched. Nothing removed.')

    print(f'{len(match)} row(s) will be removed and permanently excluded:\n')
    for _, r in match.iterrows():
        print(f"  - {str(r['resource_name'])[:72]}")
        print(f"    {r['url']}")

    if not args.yes:
        if input('\nProceed? [y/N] ').strip().lower() not in ('y', 'yes'):
            print('Aborted; nothing changed.')
            return

    new_rows = [{
        'url': r['url'],
        'resource_name': str(r['resource_name'])[:120],
        'rejected_from': r.get('resource_subtype', ''),
        'rejected_date': date.today().isoformat(),
        'reason': args.reason,
    } for _, r in match.iterrows()]

    rejected = (pd.concat([rejected, pd.DataFrame(new_rows)], ignore_index=True)
                .drop_duplicates(subset=['url'], keep='last'))
    rejected.to_csv(REJECTED, index=False)

    kept = inv[~inv.index.isin(match.index)]
    kept.to_csv(INVENTORY, index=False)

    print(f'\nInventory: {len(inv)} -> {len(kept)} rows')
    print(f'Rejection list: {len(rejected)} URLs (these will never be re-added)')
    print('\nCommit both files so the exclusion survives the next scan:')
    print(f'  git add {INVENTORY} {REJECTED} && git commit -m "Remove resource"')


if __name__ == '__main__':
    main()
