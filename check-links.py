#!/usr/bin/env python3
"""
Check every inventory URL and report which ones a visitor cannot open.

A catalogue whose links are dead is worse than a smaller working one, and the
scanners have no way to notice rot: they only ever add. Run this before
publishing, and periodically after.

Writes data/link_check.csv with a row per resource. Reports:
  ok       - 200
  gated    - 401/403: exists but needs a login, so not a public good
  missing  - 404/410
  error    - DNS failure, timeout, TLS problem
  moved    - ended somewhere unrelated after redirects

Usage:
  python3 check-links.py              # check all, write report
  python3 check-links.py --bad-only   # print only the problems
"""

import argparse
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

import pandas as pd
import requests

INV = 'data/k12_inventory_latest.csv'
REPORT = 'data/link_check.csv'
TIMEOUT = 20
WORKERS = 6
HOST_DELAY = 0.7   # polite gap between hits on the same host
_host_locks = {}

UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/120.0 Safari/537.36')


def classify(status, url, final_url):
    if status is None:
        return 'error'
    if status == 429:
        return 'ratelimited'
    if status in (401, 403):
        return 'gated'
    if status in (404, 410):
        return 'missing'
    if 200 <= status < 300:
        # A redirect that lands on a different host is usually a dead path
        # quietly bounced to a homepage.
        if final_url and urlparse(final_url).netloc != urlparse(url).netloc:
            return 'moved'
        return 'ok'
    if 300 <= status < 400:
        return 'ok'
    return 'error'


def check(row):
    url = str(row['url'] or '').strip()
    name = str(row['resource_name'])
    if not url.startswith('http'):
        return dict(resource_name=name, url=url, status='', verdict='error',
                    note='not an http url')
    s = requests.Session()
    s.headers['User-Agent'] = UA
    status, final, note = None, '', ''

    # Serialise per host and retry on 429. Hammering huggingface.co with
    # parallel workers earned a wave of 429s that looked exactly like broken
    # links - a false positive worse than no check at all.
    host = urlparse(url).netloc
    lock = _host_locks.setdefault(host, threading.Lock())

    for attempt in range(4):
        try:
            with lock:
                time.sleep(HOST_DELAY)
                # Some hosts reject HEAD; fall back to a ranged GET.
                r = s.head(url, allow_redirects=True, timeout=TIMEOUT)
                if r.status_code in (405, 501) or r.status_code >= 400:
                    r = s.get(url, allow_redirects=True, timeout=TIMEOUT,
                              headers={'Range': 'bytes=0-2048'}, stream=True)
            status, final = r.status_code, r.url
            if status != 429:
                break
            wait = float(r.headers.get('Retry-After') or (2 ** attempt) * 3)
            note = f'429, retrying after {wait:.0f}s'
            time.sleep(min(wait, 30))
        except requests.exceptions.SSLError as e:
            note = f'ssl: {str(e)[:70]}'
            break
        except requests.exceptions.ConnectionError as e:
            note = f'connection: {str(e)[:70]}'
            break
        except requests.exceptions.Timeout:
            note = 'timeout'
            break
        except Exception as e:
            note = f'{type(e).__name__}: {str(e)[:60]}'
            break
    if status == 429:
        note = 'rate limited after retries - inconclusive, not a broken link'

    verdict = classify(status, url, final)
    if verdict == 'moved':
        note = f'redirected to {final[:70]}'
    return dict(resource_name=name, url=url, status=status or '',
                verdict=verdict, note=note,
                resource_subtype=row.get('resource_subtype', ''),
                discovery_source=row.get('discovery_source', ''),
                tier=row.get('final_readiness_index_tier', ''))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bad-only', action='store_true')
    args = ap.parse_args()

    df = pd.read_csv(INV)
    rows = [r for _, r in df.iterrows()]
    print(f'Checking {len(rows)} URLs with {WORKERS} workers...\n', file=sys.stderr)

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        results = list(ex.map(check, rows))

    out = pd.DataFrame(results)
    out.to_csv(REPORT, index=False)

    counts = out['verdict'].value_counts()
    print('=== summary ===')
    for v in ('ok', 'gated', 'missing', 'moved', 'ratelimited', 'error'):
        if v in counts:
            print(f'  {v:8} {counts[v]:4}')

    bad = out[out.verdict != 'ok'].sort_values(['verdict', 'resource_name'])
    if len(bad):
        print(f'\n=== {len(bad)} problem links ===')
        for _, r in bad.iterrows():
            tier = 'curated' if 'Not Reviewed' not in str(r['tier']) else 'unreviewed'
            print(f"  [{r['verdict']:7}] {str(r['status']):4} {tier:10} "
                  f"{str(r['resource_name'])[:46]:46}")
            print(f"            {str(r['url'])[:96]}")
            if r['note']:
                print(f"            {r['note']}")
    print(f'\nFull report: {REPORT}')


if __name__ == '__main__':
    main()
