import unittest
from io import BytesIO
from unittest.mock import patch

from tool import plan_territories


class TerritoryPlannerTests(unittest.TestCase):
    def test_allocates_returned_companies_by_country_and_size(self):
        rows = [
            {"name": "A", "headquarters_country_code": "US", "company_size_from": 50, "company_size_to": 120},
            {"name": "B", "headquarters_country_code": "US", "company_size_from": 2, "company_size_to": 10},
            {"name": "C", "headquarters_country_code": "GB", "company_size_from": 1000, "company_size_to": 5000},
        ]
        result = plan_territories(rows)
        self.assertEqual(result["company_count"], 3)
        self.assertEqual(result["country_counts"], {"GB": 1, "US": 2})
        self.assertEqual(result["size_band_counts"]["51-200"], 1)

    def test_missing_or_invalid_size_is_unknown_not_zero(self):
        result = plan_territories([{"name": "A", "company_size_from": "bad"}])
        self.assertEqual(result["size_band_counts"]["unknown"], 1)
        self.assertEqual(result["country_counts"]["unknown"], 1)

    def test_empty_input_is_valid(self):
        self.assertEqual(plan_territories([])["company_count"], 0)

    def test_business_search_uses_documented_company_endpoint_and_summary_view(self):
        from tool import search_companies
        response = BytesIO(b'{"documents": [], "meta": {"coverage_percent": 100}}')
        with patch("tool.urlopen", return_value=response) as mocked:
            search_companies("US software companies", "test-key")
        request = mocked.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.brightdata.com/search/company")
        self.assertIn(b'"source": "linkedin_company"', request.data)
        self.assertIn(b'"view": "summary"', request.data)


if __name__ == "__main__":
    unittest.main()
