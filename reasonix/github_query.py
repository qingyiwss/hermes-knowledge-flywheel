import urllib.request
import json

repos = [
    "crewAIInc/crewAI",
    "microsoft/autogen",
    "geekan/MetaGPT",
    "OpenBMB/ChatDev",
    "OpenBMB/AgentVerse",
    "camel-ai/camel",
    "ag2ai/ag2",
    "microsoft/TaskWeaver",
    "joaomdmoura/crewAI",
    "Significant-Gravitas/AutoGPT",
    "langchain-ai/langgraph",
]

for repo in repos:
    try:
        url = f"https://api.github.com/repos/{repo}"
        req = urllib.request.Request(url, headers={"User-Agent": "Hermes"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            print(f"\n=== {repo} ===")
            print(f"Stars: {data.get('stargazers_count')}")
            print(f"Language: {data.get('language')}")
            print(f"Description: {data.get('description')}")
            print(f"Forks: {data.get('forks_count')}")
            print(f"Open Issues: {data.get('open_issues_count')}")
            print(f"Last pushed: {data.get('pushed_at')}")
            print(f"Topics: {data.get('topics', [])}")
            print(f"License: {data.get('license', {}).get('spdx_id', 'N/A') if data.get('license') else 'N/A'}")
    except Exception as e:
        print(f"\n=== {repo} === ERROR: {e}")

print("\n\nDone!")
