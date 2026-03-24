#!/usr/bin/env python3
import json
from pathlib import Path

BASE = Path('/data/app/world.unxai.top')
COUNTRIES = BASE / 'data' / 'countries.json'
REPORT = BASE / 'data' / 'validation_report.json'

countries = json.loads(COUNTRIES.read_text())
report = {
    'countries': len(countries),
    'models_total': 0,
    'verified_models': 0,
    'unverified_models': 0,
    'issues': []
}

for country in countries:
    for model in country.get('models', []):
        report['models_total'] += 1
        if model.get('verified'):
            report['verified_models'] += 1
        else:
            report['unverified_models'] += 1
            report['issues'].append({
                'country': country.get('name'),
                'model': model.get('name'),
                'company': model.get('company'),
                'reason': 'unverified'
            })
        if not model.get('source'):
            report['issues'].append({
                'country': country.get('name'),
                'model': model.get('name'),
                'company': model.get('company'),
                'reason': 'missing_source'
            })

REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2))
print(json.dumps({
    'countries': report['countries'],
    'models_total': report['models_total'],
    'verified_models': report['verified_models'],
    'unverified_models': report['unverified_models']
}, ensure_ascii=False))
