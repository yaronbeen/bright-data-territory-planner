# Bright Data Territory Planner

Turn a bounded Bright Data Business Search company result set into a first-pass territory sizing brief by headquarters country and employee-size band. It helps a sales-ops or channel team decide where to validate coverage and capacity next. It is not a prospect list, contact finder, lead scorer, or census.

## Synthetic Example -> Decision

`sample.json` contains three invented company records. Run it and the report shows two US and one CA company, split into size bands. A sales-ops lead can use that distribution to propose a US/Canada territory test, then validate actual account capacity and coverage in their CRM. The sample is synthetic and not a market estimate.

## Workflow

1. Search Bright Data Business Search for a bounded company segment.
2. Group only returned company summaries by country and employee-size midpoint.
3. Review `search_meta.coverage_percent` and the caveats before using the counts.
4. Take the territory hypothesis to the CRM and validate ownership/capacity there.

## Setup

Python 3.10+; runtime uses only the standard library.

```bash
cp .env.example .env
export BRIGHT_DATA_API_KEY="your-key"
```

Business Search is early access and requires account allowlisting. Create an API key in [Bright Data settings](https://brightdata.com/cp/setting/users). For API access and request fields see the official [Business Search overview](https://docs.brightdata.com/products/business-search/introduction.md) and [quickstart](https://docs.brightdata.com/products/business-search/quickstart.md).

## Run

```bash
python3 tool.py sample.json
BRIGHT_DATA_API_KEY="your-key" python3 tool.py --live "US and Canada software companies with 50 to 500 employees"
python3 -m unittest -v
```

The live command makes one `POST /search/company` Instant query and may incur usage charges. It uses `source: linkedin_company`, `view: summary`, and requests a maximum of 10 results, matching the documented safe page size. When 10 documents are returned, output marks `result_limit_reached`; this means results may be capped, not that the API confirmed additional matches. Credentials are read from the environment, never saved. The programmatic `search_companies` function accepts a key so applications can inject it without putting secrets on the command line. Requests are not automatically retried because repeating a billable request may duplicate usage.

## Outputs

JSON includes returned company count, country counts, employee-size bands, a limitation note, and (for live queries) the API's response metadata and `result_limit_reached` flag. Size bands use the midpoint of each returned low/high employee range as a heuristic; `>1000 midpoint` means the computed midpoint exceeds 1,000. Missing/invalid employee ranges are `unknown`; country counts refer only to returned records. `coverage_percent` describes index/query response coverage, not the share of the real-world market; group counts are incomplete when index coverage is partial.

On live HTTP/network failure, the CLI writes a JSON object to stderr with an `error` containing a stable `code`, sanitized `message`, and `retryable: false`, then exits 1. Success JSON remains on stdout. No automatic retry is made.

## Differentiation

The account already has LinkedIn profile/job scraping, contact enrichment, outreach, and buyer-intent workflows (for example `bright-data-linkedin-outreach`, `LinkedinJobsAutomation`, `upwork-scanner`, and the Bright Data social intent finders). This tool does none of those: it summarizes returned company records into aggregate territory-sizing buckets and never exports people or drafts outreach. The WIP backlog mentions funding and hiring signals, not territory allocation; this is an adjacent but different decision.

## FAQ

**Does this identify all companies in a region?** No. Business Search results are an index sample; its `matched` field is not a census. Coverage can be partial and the index refreshes daily.

**Does it find contacts?** No. It requests company summaries only.

**Can I use it without Business Search access?** Yes. The bundled synthetic sample runs offline; live use requires early access.

## Compliance and limitations

Use the API only with authorized account access and in accordance with Bright Data terms and applicable privacy laws. Company counts are descriptive of returned data, not market size, sales capacity, or a recommended quota. Human review is required before territory decisions. No personal contact fields are requested or retained.

## Bright Data

Powered by [Bright Data Business Search](https://brightdata.com/products/business-search). MIT licensed.
