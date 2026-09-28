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

    def test_midpoint_threshold_boundary_is_unambiguous(self):
        result = plan_territories([
            {"company_size_from": 900, "company_size_to": 1100},
            {"company_size_from": 1001, "company_size_to": 1001},
        ])
        self.assertEqual(result["size_band_counts"]["201-1000"], 1)
        self.assertEqual(result["size_band_counts"][">1000 midpoint"], 1)

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
        self.assertIn(b'"limit": 10', request.data)
        self.assertNotIn(b'"limit": 100', request.data)

    def test_output_discloses_midpoint_heuristic_and_limit_reached(self):
        from tool import main
        from contextlib import redirect_stdout
        from io import StringIO
        response = {"documents": [{"data": {}}] * 10, "meta": {}}
        with patch("tool.search_companies", return_value=response), patch.dict("os.environ", {"BRIGHT_DATA_API_KEY": "secret"}), patch("sys.argv", ["tool.py", "--live", "query"]), redirect_stdout(StringIO()) as output:
            main()
        result = __import__("json").loads(output.getvalue())
        self.assertTrue(result["result_limit_reached"])
        self.assertIn("midpoint", result["decision_note"].lower())

    def test_live_cli_errors_are_structured_and_do_not_retry_or_leak_secrets(self):
        from contextlib import redirect_stderr
        from io import StringIO
        from urllib.error import URLError
        from tool import main
        with patch("tool.search_companies", side_effect=URLError("secret-token")), patch.dict("os.environ", {"BRIGHT_DATA_API_KEY": "secret-token"}), patch("sys.argv", ["tool.py", "--live", "query"]), redirect_stderr(StringIO()) as error:
            with self.assertRaises(SystemExit) as exit_error:
                main()
        payload = __import__("json").loads(error.getvalue())
        self.assertEqual(exit_error.exception.code, 1)
        self.assertFalse(payload["error"]["retryable"])
        self.assertNotIn("secret-token", error.getvalue())


if __name__ == "__main__":
    unittest.main()
