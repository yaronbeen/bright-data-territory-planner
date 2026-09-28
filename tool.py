"""Turn company search results into a territory-sizing brief."""
import json
import os
import sys
from collections import Counter
from urllib.request import Request, urlopen


def plan_territories(records):
    countries, bands = Counter(), Counter()
    for row in records:
        raw_country = row.get("headquarters_country_code")
        country = raw_country.strip().upper() if isinstance(raw_country, str) and raw_country.strip() else "unknown"
        countries[country] += 1
        low, high = row.get("company_size_from"), row.get("company_size_to")
        try:
            midpoint = (int(low) + int(high)) / 2
        except (TypeError, ValueError):
            bands["unknown"] += 1
            continue
        bands["1-50" if midpoint <= 50 else "51-200" if midpoint <= 200 else "201-1000" if midpoint <= 1000 else "1000+"] += 1
    return {"company_count": len(records), "country_counts": dict(sorted(countries.items())), "size_band_counts": dict(sorted(bands.items())), "decision_note": "Counts describe only returned records. Business Search coverage_percent is index/query response coverage, not the share of the real-world market; grouping counts are incomplete when index coverage is partial."}


def search_companies(query, api_key):
    payload = {"source": "linkedin_company", "mode": "instant", "query": query, "offset": 0, "limit": 10, "view": "summary"}
    request = Request("https://api.brightdata.com/search/company", data=json.dumps(payload).encode(), headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"})
    with urlopen(request, timeout=45) as response:
        data = json.load(response)
    return data


def main():
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python3 tool.py SAMPLE.json | --live QUERY")
    if sys.argv[1] == "--live":
        if len(sys.argv) != 3 or not os.getenv("BRIGHT_DATA_API_KEY"):
            raise SystemExit("Set BRIGHT_DATA_API_KEY and provide a company query")
        response = search_companies(sys.argv[2], os.environ["BRIGHT_DATA_API_KEY"])
        result = plan_territories([item.get("data", {}) for item in response.get("documents", [])])
        result["search_meta"] = response.get("meta", {})
    else:
        with open(sys.argv[1], encoding="utf-8") as source:
            result = plan_territories(json.load(source))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
