#!/usr/bin/env python3
import json
from collections import Counter
from pathlib import Path

BASE = Path('/data/app/world.unxai.top')
COUNTRIES = BASE / 'data' / 'countries.json'
SUMMARY = BASE / 'data' / 'family_summary.json'


def main():
    countries = json.loads(COUNTRIES.read_text())
    summary = []
    for country in countries:
        counter = Counter()
        verified_counter = Counter()
        pending_counter = Counter()
        for model in country.get('models', []):
            family = model.get('family') or model.get('company') or 'Unknown'
            counter[family] += 1
            if model.get('verified'):
                verified_counter[family] += 1
            else:
                pending_counter[family] += 1
        families = []
        for family, count in counter.most_common():
            families.append({
                'family': family,
                'count': count,
                'verified_count': verified_counter[family],
                'pending_count': pending_counter[family],
            })
        summary.append({
            'country': country.get('name'),
            'continent': country.get('continent'),
            'families': families,
        })
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print(json.dumps({'ok': True, 'countries': len(summary)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
