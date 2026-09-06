#!/usr/bin/env python3
"""Recover exact historical Bungie D1 Armory pages through curl/IPv4.

The first Common Crawl probe used Python urllib with short concurrent timeouts. On
GitHub-hosted runners every historical index query timed out before returning, so
that run established a transport failure, not absence of archived Armory records.

This alternate transport deliberately uses curl with IPv4, longer bounded timeouts,
and low concurrency. It first asks exact URL variants, then only for collections
that returned no exact record tries narrowly item-specific prefixes. Any accepted
CDX row must still parse back to the exact requested unsigned item id, and WARC bytes
are fetched from the exact filename/offset/length tuple returned by Common Crawl.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import gzip
import hashlib
import json
import re
import subprocess
import urllib.parse
from pathlib import Path

KEYWORDS = ('ArmoryDetailPage.model', 'defaultArmor', 'gearAndDefaultArmor')
UA = 'd1-reversal-evidence/2.0 (+https://github.com/lizardpeter/destiny-1)'


def curl(url: str, *, range_header: str | None = None, max_time: int = 60):
    cmd = [
        'curl', '-4', '-L', '-sS', '--fail-with-body',
        '--connect-timeout', '20', '--max-time', str(max_time),
        '--retry', '1', '--retry-delay', '1',
        '-A', UA, '-H', 'Accept: */*',
    ]
    if range_header:
        cmd += ['-H', f'Range: {range_header}']
    cmd.append(url)
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.returncode, p.stdout, p.stderr.decode('utf-8', errors='replace')


def collection_year(cid: str):
    m = re.search(r'CC-MAIN-(20\d\d)-', cid)
    return int(m.group(1)) if m else None


def parse_item(url: str):
    try:
        q = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query, keep_blank_values=True)
        v = q.get('item')
        return int(v[0]) if v and len(v) == 1 and v[0].isdigit() else None
    except Exception:
        return None


def armory_path(url: str):
    try:
        return urllib.parse.urlsplit(url).path.lower() == '/en/armory/detail'
    except Exception:
        return False


def cdx_query(api: str, target: str, match_type: str):
    query = urllib.parse.urlencode({
        'url': target,
        'output': 'json',
        'matchType': match_type,
        'filter': 'status:200',
    })
    sep = '&' if '?' in api else '?'
    code, body, err = curl(api + sep + query, max_time=70)
    rows = []
    if code == 0:
        for line in body.decode('utf-8', errors='replace').splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                pass
    return code, err, rows, len(body)


def decode_warc(raw: bytes):
    try:
        data = gzip.decompress(raw)
    except Exception:
        data = raw
    p = data.find(b'\r\n\r\n')
    split = 4
    if p < 0:
        p = data.find(b'\n\n')
        split = 2
    if p >= 0:
        data = data[p + split:]
    if data.startswith(b'HTTP/'):
        p = data.find(b'\r\n\r\n')
        split = 4
        if p < 0:
            p = data.find(b'\n\n')
            split = 2
        if p >= 0:
            data = data[p + split:]
    return data


def snippets(text: str, radius: int = 2500):
    low = text.lower()
    out = []
    for keyword in KEYWORDS:
        start = 0
        while True:
            i = low.find(keyword.lower(), start)
            if i < 0:
                break
            out.append({
                'keyword': keyword,
                'offset': i,
                'text': text[max(0, i - radius): min(len(text), i + len(keyword) + radius)],
            })
            start = i + len(keyword)
            if len(out) >= 30:
                return out
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--item', type=int, required=True)
    ap.add_argument('--name', default='')
    ap.add_argument('--start-year', type=int, default=2015)
    ap.add_argument('--end-year', type=int, default=2017)
    ap.add_argument('--max-collections', type=int, default=18)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--max-records', type=int, default=20)
    ap.add_argument('-o', '--out-dir', type=Path, required=True)
    a = ap.parse_args()
    a.out_dir.mkdir(parents=True, exist_ok=True)

    code, body, err = curl('https://index.commoncrawl.org/collinfo.json', max_time=45)
    report = {
        'schema': 'd1_commoncrawl_armory_curl_probe/v1',
        'item': a.item,
        'name': a.name,
        'years': [a.start_year, a.end_year],
        'collinfo_curl_code': code,
        'collinfo_error': err,
        'queries': [],
        'candidate_count': 0,
        'candidates': [],
        'records': [],
        'selected': None,
        'snippets': [],
        'policy': 'Only exact requested item-id Armory captures fetched from exact Common Crawl CDX WARC tuples are accepted.',
    }
    (a.out_dir / 'collinfo.json').write_bytes(body)
    if code != 0:
        (a.out_dir / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report, indent=2))
        return 0

    collections = json.loads(body.decode('utf-8-sig'))
    collections = [
        c for c in collections
        if collection_year(c.get('id', '')) is not None
        and a.start_year <= collection_year(c['id']) <= a.end_year
        and (c.get('cdx-api') or c.get('index'))
    ]
    # Common Crawl returns newest first; keep the bounded newest historical set.
    collections = collections[:a.max_collections]

    hosts = ('www.bungie.net', 'bungie.net')
    schemes = ('https', 'http')
    query_forms = (
        f'type=item&item={a.item}',
        f'item={a.item}&type=item',
        f'item={a.item}',
    )
    targets = [
        f'{scheme}://{host}/en/Armory/Detail?{q}'
        for scheme in schemes for host in hosts for q in query_forms
    ]
    # CDX commonly stores scheme-less URL keys too.
    targets += [
        f'{host}/en/Armory/Detail?{q}'
        for host in hosts for q in query_forms
    ]

    tasks = []
    for c in collections:
        api = c.get('cdx-api') or c.get('index')
        for target in targets:
            tasks.append((c['id'], api, target, 'exact'))

    def run_query(task):
        cid, api, target, match_type = task
        rc, qe, rows, size = cdx_query(api, target, match_type)
        return {
            'collection': cid,
            'api': api,
            'target': target,
            'match_type': match_type,
            'curl_code': rc,
            'error': qe,
            'response_bytes': size,
            'row_count': len(rows),
        }, rows

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, a.workers)) as pool:
        for result in pool.map(run_query, tasks):
            results.append(result)

    seen = set()
    candidates = []
    exact_found_by_collection = set()
    for qrec, rows in results:
        report['queries'].append(qrec)
        if rows:
            exact_found_by_collection.add(qrec['collection'])
        for row in rows:
            url = row.get('url', '')
            if not armory_path(url) or parse_item(url) != a.item:
                continue
            key = (row.get('filename'), str(row.get('offset')), str(row.get('length')))
            if key in seen:
                continue
            seen.add(key)
            row = dict(row)
            row['collection'] = qrec['collection']
            candidates.append(row)

    # If exact URL variants found nothing, use narrowly item-specific prefix forms.
    fallback_tasks = []
    for c in collections:
        if c['id'] in exact_found_by_collection:
            continue
        api = c.get('cdx-api') or c.get('index')
        for host in hosts:
            for prefix in (
                f'{host}/en/Armory/Detail?type=item&item={a.item}',
                f'{host}/en/Armory/Detail?item={a.item}',
            ):
                fallback_tasks.append((c['id'], api, prefix, 'prefix'))
    if fallback_tasks:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, a.workers)) as pool:
            for qrec, rows in pool.map(run_query, fallback_tasks):
                report['queries'].append(qrec)
                for row in rows:
                    url = row.get('url', '')
                    if not armory_path(url) or parse_item(url) != a.item:
                        continue
                    key = (row.get('filename'), str(row.get('offset')), str(row.get('length')))
                    if key in seen:
                        continue
                    seen.add(key)
                    row = dict(row)
                    row['collection'] = qrec['collection']
                    candidates.append(row)

    candidates.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    report['candidate_count'] = len(candidates)
    report['candidates'] = candidates[:200]

    for index, row in enumerate(candidates[:a.max_records]):
        try:
            off = int(row['offset'])
            length = int(row['length'])
            filename = row['filename']
        except Exception as e:
            report['records'].append({'candidate': row, 'error': f'bad CDX tuple: {e}'})
            continue
        rc, raw, fetch_err = curl(
            'https://data.commoncrawl.org/' + filename,
            range_header=f'bytes={off}-{off + length - 1}',
            max_time=90,
        )
        record = {
            'collection': row['collection'],
            'timestamp': row.get('timestamp'),
            'url': row.get('url'),
            'filename': filename,
            'offset': off,
            'length': length,
            'curl_code': rc,
            'transport_error': fetch_err,
            'fetched_bytes': len(raw),
            'sha256': hashlib.sha256(raw).hexdigest(),
        }
        report['records'].append(record)
        if rc != 0:
            continue
        decoded = decode_warc(raw)
        text = decoded.decode('utf-8', errors='replace')
        hits = snippets(text)
        path = a.out_dir / f"capture_{index:02d}_{row.get('timestamp', 'unknown')}.html"
        path.write_bytes(decoded)
        record['decoded_body_bytes'] = len(decoded)
        record['decoded_body_sha256'] = hashlib.sha256(decoded).hexdigest()
        record['snippet_keywords'] = [x['keyword'] for x in hits]
        if report['selected'] is None or hits:
            report['selected'] = record
            report['selected_file'] = path.name
            report['snippets'] = hits
        if hits:
            break

    (a.out_dir / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({
        'item': a.item,
        'name': a.name,
        'collections': len(collections),
        'queries': len(report['queries']),
        'transport_successes': sum(1 for q in report['queries'] if q['curl_code'] == 0),
        'candidate_count': report['candidate_count'],
        'selected': report['selected'],
        'snippet_keywords': [x['keyword'] for x in report['snippets']],
    }, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
