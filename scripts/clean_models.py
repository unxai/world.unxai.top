#!/usr/bin/env python3
import json
import re
from pathlib import Path

BASE = Path('/data/app/world.unxai.top')
COUNTRIES = BASE / 'data' / 'countries.json'

PREFIX_ALIASES = {
    'Qwen': 'Qwen',
    'Z.ai': 'GLM',
    'MoonshotAI': 'Kimi',
    'DeepSeek': 'DeepSeek',
    'MiniMax': 'MiniMax',
    'StepFun': 'Step',
    'Baidu': 'ERNIE',
    'Tencent': 'Hunyuan',
    'Google': 'Gemini',
    'OpenAI': 'GPT',
    'Anthropic': 'Claude',
    'Mistral': 'Mistral',
    'xAI': 'Grok',
    'Cohere': 'Command',
}


def tidy_spaces(value: str) -> str:
    return re.sub(r'\s+', ' ', (value or '').strip())


def clean_display_name(name: str) -> str:
    value = tidy_spaces(name)
    value = re.sub(r'\s*\(free\)', '', value, flags=re.I)
    value = re.sub(r'\s+', ' ', value)
    if ':' in value:
        prefix, rest = [part.strip() for part in value.split(':', 1)]
        canonical = PREFIX_ALIASES.get(prefix, prefix)
        if rest.lower().startswith(canonical.lower() + ' '):
            value = rest
        elif rest.lower() == canonical.lower():
            value = rest
        else:
            value = rest
    return tidy_spaces(value)


def infer_family(display_name: str, company: str) -> str:
    text = display_name.lower()
    rules = [
        ('qwen', 'Qwen'),
        ('glm', 'GLM'),
        ('kimi', 'Kimi'),
        ('deepseek', 'DeepSeek'),
        ('ernie', 'ERNIE'),
        ('hunyuan', 'Hunyuan'),
        ('gemini', 'Gemini'),
        ('gemma', 'Gemma'),
        ('gpt', 'GPT'),
        ('o1', 'OpenAI o-series'),
        ('o3', 'OpenAI o-series'),
        ('o4', 'OpenAI o-series'),
        ('claude', 'Claude'),
        ('mistral', 'Mistral'),
        ('ministral', 'Ministral'),
        ('mixtral', 'Mixtral'),
        ('codestral', 'Codestral'),
        ('devstral', 'Devstral'),
        ('grok', 'Grok'),
        ('command', 'Command'),
        ('minimax', 'MiniMax'),
        ('step', 'Step'),
        ('llama', 'Llama'),
    ]
    for needle, family in rules:
        if needle in text:
            return family
    return company or 'Unknown'


def main():
    countries = json.loads(COUNTRIES.read_text())
    for country in countries:
        for model in country.get('models', []):
            display_name = clean_display_name(model.get('name', ''))
            model['display_name'] = display_name
            model['family'] = infer_family(display_name, model.get('company', ''))

    COUNTRIES.write_text(json.dumps(countries, ensure_ascii=False, indent=2))
    print(json.dumps({'ok': True, 'countries': len(countries)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
