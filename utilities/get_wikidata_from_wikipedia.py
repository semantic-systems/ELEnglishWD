from typing import List

import requests


def get_wikidata_from_wikipedia(wikipedia_identifiers: List[str]):
    concatenated_identifiers = "|".join(wikipedia_identifiers)
    headers = {"User-Agent": "My User Agent 1.0"}
    result = requests.get(
        f"https://en.wikipedia.org/w/api.php?action=query&redirects&prop=pageprops&titles={concatenated_identifiers}&format=json",
        headers=headers,
    )
    result = result.json()
    if result["query"]["normalized"]:
        normalized = result["query"]["normalized"]
        normalized = {item["to"]: item["from"] for item in normalized}
    else:
        normalized = {}

    if "redirects" in result["query"]:
        redirects = result["query"]["redirects"]
        redirects = {item["to"]: item["from"] for item in redirects}
    else:
        redirects = {}

    if result["query"]["pages"]:
        result = result["query"]["pages"]
        result = [item for item in result.values()]
    assignments = {}

    for item in result:
        try:
            title = item["title"]
            if title in redirects:
                title = redirects[title]
            if title in normalized:
                title = normalized[title]

            assignments[title] = item["pageprops"]["wikibase_item"]
        except Exception as e:
            pass

    return assignments
