import requests

def get_wikipedia_full_text():
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "extracts",
        "explaintext": True,
        "titles": "Department_of_Economy,_Planning,_and_Development",
        "format": "json",
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        pages = data.get("query", {}).get("pages", {})
        page = next(iter(pages.values()))
        full_text = page.get("extract", "No content found.")
        return full_text
    else:
        return "Failed to fetch Wikipedia page content."
