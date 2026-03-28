#!/usr/bin/env python3
import json
import re
import urllib.request
from pathlib import Path

BASE = Path('/data/app/world.unxai.top')
COUNTRIES = BASE / 'data' / 'countries.json'
MAP = BASE / 'data' / 'company_country_map.json'
OUT = BASE / 'data' / 'model_candidates.json'

ALIASES = {
    'openai': 'OpenAI',
    'anthropic': 'Anthropic',
    'google': 'Google',
    'meta-llama': 'Meta',
    'meta': 'Meta',
    'x-ai': 'xAI',
    'xai': 'xAI',
    'cohere': 'Cohere',
    'mistralai': 'Mistral AI',
    'mistral': 'Mistral AI',
    'ai21': 'AI21 Labs',
    'ai21labs': 'AI21 Labs',
    'naver': 'NAVER',
    'kakao': 'Kakao',
    'preferred-networks': 'Preferred Networks',
    'preferrednetworks': 'Preferred Networks',
    'qwen': '阿里云',
    'alibaba': '阿里云',
    'baidu': '百度',
    'tencent': '腾讯',
    'bytedance': '字节跳动',
    'bytedance-seed': '字节跳动',
    'deepseek': 'DeepSeek',
    'z-ai': '智谱',
    'zai': '智谱',
    'moonshotai': 'Moonshot AI',
    'minimax': 'MiniMax',
    'stepfun': '阶跃星辰',
}

COMPANY_DISPLAY = {
    '阿里云': '阿里云',
    '百度': '百度',
    '腾讯': '腾讯',
    '字节跳动': '字节跳动',
    'DeepSeek': 'DeepSeek',
    '智谱': '智谱',
    'Moonshot AI': 'Moonshot AI',
    'MiniMax': 'MiniMax',
    '阶跃星辰': '阶跃星辰',
}


def slug(value: str) -> str:
    return re.sub(r'[^a-z0-9]+', '', (value or '').strip().lower())


def fetch_openrouter():
    urls = [
        'https://openrouter.ai/api/v1/models',
        'https://openrouter.ai/api/frontend/models'
    ]
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=20) as r:
                data = json.loads(r.read().decode('utf-8'))
                return url, data
        except Exception:
            continue
    return None, None


def resolve_company(raw_company: str, company_map: dict):
    key = slug(raw_company)
    canonical = ALIASES.get(key, raw_company)
    if canonical in company_map:
        return canonical, company_map[canonical]

    for name, country in company_map.items():
        if slug(name) == key:
            return name, country
    return canonical, None


def extract_raw_company(name: str, model_id: str, item: dict):
    raw_company = ''
    if '/' in model_id:
        raw_company = model_id.split('/')[0]
    if not raw_company and ':' in name:
        raw_company = name.split(':', 1)[0].strip()
    if not raw_company:
        raw_company = item.get('top_provider', {}).get('name', '') if isinstance(item.get('top_provider'), dict) else ''
    if not raw_company:
        architecture = item.get('architecture') or {}
        if isinstance(architecture, dict):
            raw_company = architecture.get('modality', '') or architecture.get('tokenizer', '') or ''
    return raw_company.strip()


def normalize_openrouter(payload, company_map):
    items = payload.get('data') if isinstance(payload, dict) else None
    if not isinstance(items, list):
        return []
    out = []
    for item in items:
        name = item.get('name') or item.get('id') or ''
        model_id = item.get('id') or name
        raw_company = extract_raw_company(name, model_id, item)
        canonical_company, country = resolve_company(raw_company, company_map)
        out.append({
            'name': name,
            'company': COMPANY_DISPLAY.get(canonical_company, canonical_company or '未知厂商'),
            'company_country': country,
            'type': '大语言模型',
            'source': 'OpenRouter',
            'source_id': model_id
        })
    return out


def merge_into_countries(candidates, countries):
    by_name = {c['name']: c for c in countries}
    merged = 0
    skipped = 0
    for item in candidates:
        country_name = item.get('company_country')
        if not country_name or country_name not in by_name:
            skipped += 1
            continue
        country = by_name[country_name]
        models = country.setdefault('models', [])
        exists = any(
            (m.get('name') == item['name']) or
            (m.get('source_id') and m.get('source_id') == item['source_id'])
            for m in models
        )
        if exists:
            skipped += 1
            continue
        models.append({
            'name': item['name'],
            'company': item['company'],
            'type': item['type'],
            'source': item['source'],
            'source_id': item['source_id'],
            'company_country': country_name,
            'verified': False,
        })
        merged += 1
    for country in countries:
        country['model_count'] = len(country.get('models', []))
        country['has_models'] = country['model_count'] > 0
    return countries, merged, skipped


def main():
    company_map = json.loads(MAP.read_text())
    countries = json.loads(COUNTRIES.read_text())
    source_url, payload = fetch_openrouter()
    if payload is None:
        print(json.dumps({'ok': False, 'error': 'openrouter fetch failed'}, ensure_ascii=False))
        return
    candidates = normalize_openrouter(payload, company_map)
    OUT.write_text(json.dumps({
        'source': source_url,
        'count': len(candidates),
        'mapped_count': sum(1 for item in candidates if item.get('company_country')),
        'items': candidates[:500]
    }, ensure_ascii=False, indent=2))
    updated, merged, skipped = merge_into_countries(candidates, countries)
    COUNTRIES.write_text(json.dumps(updated, ensure_ascii=False, indent=2))
    print(json.dumps({
        'ok': True,
        'source': source_url,
        'candidate_count': len(candidates),
        'mapped_count': sum(1 for item in candidates if item.get('company_country')),
        'merged_count': merged,
        'skipped_count': skipped,
        'country_count': len(updated)
    }, ensure_ascii=False))

if __name__ == '__main__':
    main()
