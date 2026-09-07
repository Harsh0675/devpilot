import json
import os
import urllib.error
import urllib.request


PROVIDERS = {
    'openai': 'openai-compatible',
    'openai-compatible': 'openai-compatible',
    'groq': 'openai-compatible',
    'together': 'openai-compatible',
    'mistral': 'openai-compatible',
    'deepseek': 'openai-compatible',
    'qwen': 'openai-compatible',
    'openrouter': 'openai-compatible',
    'ollama': 'ollama',
    'anthropic': 'anthropic',
    'gemini': 'gemini',
}

DEFAULT_BASE_URLS = {
    'openai-compatible': 'https://api.openai.com/v1',
    'ollama': 'http://localhost:11434',
    'anthropic': 'https://api.anthropic.com',
    'gemini': 'https://generativelanguage.googleapis.com',
}


def provider_name(value=None):
    value = (value or os.getenv('DEVPILOT_PROVIDER') or 'openai-compatible').lower().strip()
    return PROVIDERS.get(value, value)


def _key(provider):
    names = {
        'openai-compatible': ('DEVPILOT_API_KEY', 'OPENAI_API_KEY'),
        'ollama': ('DEVPILOT_API_KEY',),
        'anthropic': ('DEVPILOT_API_KEY', 'ANTHROPIC_API_KEY'),
        'gemini': ('DEVPILOT_API_KEY', 'GEMINI_API_KEY', 'GOOGLE_API_KEY'),
    }
    for name in names.get(provider, ('DEVPILOT_API_KEY',)):
        if os.getenv(name):
            return os.getenv(name)
    return None


def _request(url, payload, headers=None, timeout=180):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers or {'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode()), None
    except urllib.error.HTTPError as exc:
        return None, f'LLM API error {exc.code}: {exc.read().decode(errors="ignore")[:1200]}'
    except (urllib.error.URLError, TimeoutError) as exc:
        return None, f'LLM connection error: {exc}'
    except (ValueError, UnicodeError) as exc:
        return None, f'Invalid LLM response: {exc}'


def chat(messages, model=None, provider=None, base_url=None, timeout=180, temperature=0.2):
    provider = provider_name(provider)
    model = model or os.getenv('DEVPILOT_MODEL') or 'gpt-4o-mini'
    base = (base_url or os.getenv('DEVPILOT_BASE_URL') or DEFAULT_BASE_URLS.get(provider, '')).rstrip('/')
    key = _key(provider)

    if provider == 'openai-compatible':
        if not key:
            return None, 'No API key configured. Set DEVPILOT_API_KEY or the provider-specific key.'
        data, error = _request(base + '/chat/completions', {'model': model, 'messages': messages, 'temperature': temperature}, {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json', 'User-Agent': 'DevPilot/0.7.0'}, timeout)
        if error:
            return None, error
        try:
            return data['choices'][0]['message']['content'], None
        except (KeyError, IndexError, TypeError):
            return None, 'Provider returned an unsupported chat response format.'

    if provider == 'ollama':
        data, error = _request(base + '/api/chat', {'model': model, 'messages': messages, 'stream': False, 'options': {'temperature': temperature}}, {'Content-Type': 'application/json'}, timeout)
        if error:
            return None, error
        try:
            return data['message']['content'], None
        except (KeyError, TypeError):
            return None, 'Ollama returned an unsupported response format.'

    if provider == 'anthropic':
        if not key:
            return None, 'Set ANTHROPIC_API_KEY or DEVPILOT_API_KEY.'
        system = '\n'.join(m['content'] for m in messages if m.get('role') == 'system')
        user_messages = [m for m in messages if m.get('role') != 'system']
        payload = {'model': model, 'max_tokens': 8192, 'temperature': temperature, 'messages': user_messages}
        if system:
            payload['system'] = system
        data, error = _request(base + '/v1/messages', payload, {'x-api-key': key, 'anthropic-version': '2023-06-01', 'content-type': 'application/json', 'User-Agent': 'DevPilot/0.7.0'}, timeout)
        if error:
            return None, error
        try:
            return ''.join(x.get('text', '') for x in data['content'] if x.get('type') == 'text'), None
        except (KeyError, TypeError):
            return None, 'Anthropic returned an unsupported response format.'

    if provider == 'gemini':
        if not key:
            return None, 'Set GEMINI_API_KEY, GOOGLE_API_KEY, or DEVPILOT_API_KEY.'
        contents = []
        for m in messages:
            role = 'model' if m.get('role') == 'assistant' else 'user'
            contents.append({'role': role, 'parts': [{'text': m.get('content', '')}]})
        url = f'{base}/v1beta/models/{model}:generateContent?key={key}'
        data, error = _request(url, {'contents': contents, 'generationConfig': {'temperature': temperature}}, {'Content-Type': 'application/json', 'User-Agent': 'DevPilot/0.7.0'}, timeout)
        if error:
            return None, error
        try:
            return data['candidates'][0]['content']['parts'][0]['text'], None
        except (KeyError, IndexError, TypeError):
            return None, 'Gemini returned an unsupported response format.'

    return None, f'Unsupported provider: {provider}'
