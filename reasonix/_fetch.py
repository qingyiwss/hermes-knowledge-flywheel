import urllib.request, json, base64, sys

proxy = 'http://127.0.0.1:7890'
proxy_handler = urllib.request.ProxyHandler({'http': proxy, 'https': proxy})
opener = urllib.request.build_opener(proxy_handler)

targets = [
    ('shareAI-lab/learn-claude-code', 'lc'),
    ('Panniantong/Agent-Reach', 'ar'),
]

for repo, label in targets:
    url = f'https://api.github.com/repos/{repo}/readme'
    req = urllib.request.Request(url, headers={'User-Agent': 'Hermes-Agent'})
    try:
        with opener.open(req, timeout=15) as r:
            d = json.loads(r.read())
            c = base64.b64decode(d['content']).decode('utf-8', errors='ignore')
            path = f'/c/Users/admin/hermes-knowledge-flywheel/notes/_{label}-readme.md'
            with open(path, 'w', encoding='utf-8') as f:
                f.write(c)
            print(f'{label}: OK ({len(c)} chars)')
    except Exception as e:
        print(f'{label}: {e}')
