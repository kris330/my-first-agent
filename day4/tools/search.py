import requests


def web_search(query: str, max_results: int = 3) -> str:
    url = "https://api.duckduckgo.com/"
    params = {"q": query, "format": "json", "no_html": "1", "skip_disambig": "1"}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        results = []
        if data.get("AbstractText"):
            results.append(f"摘要：{data['AbstractText']}")
        for topic in data.get("RelatedTopics", [])[:max_results]:
            if isinstance(topic, dict) and topic.get("Text"):
                results.append(f"- {topic['Text']}")
        return "\n".join(results) if results else f"没有找到「{query}」的结果"
    except requests.Timeout:
        return "搜索超时，请稍后重试"
    except Exception as e:
        return f"搜索出错：{e}"
