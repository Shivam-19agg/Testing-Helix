import unittest
from unittest.mock import patch

from finops_agent.finops_agent.nodes.analysis.strategic_caching import strategic_caching_analysis_node

class TestStrategicCachingAnalysisNode(unittest.TestCase):

    @patch('finops_agent.finops_agent.tools.azure.execute_kql_query')
    def test_caching_recommendation_success_with_mixed_data(self, mock_execute_kql):
        """
        Tests that recommendations are correctly generated for GET operations
        while non-GET operations are ignored.
        """
        # --- Arrange ---
        # Mock the KQL query result
        mock_execute_kql.return_value = [
            {
                "OperationId": "get-user", "ApiId": "/apis/user-api",
                "RequestMethod": "GET", "RequestCount": 5000, "AvgBackendResponseTime": 0.4
            },
            {
                "OperationId": "update-user", "ApiId": "/apis/user-api",
                "RequestMethod": "PUT", "RequestCount": 2000, "AvgBackendResponseTime": 0.6
            },
            {
                "OperationId": "get-settings", "ApiId": "/apis/settings-api",
                "RequestMethod": "GET", "RequestCount": 10000, "AvgBackendResponseTime": 0.3
            }
        ]

        initial_state = {"resources": ["/sub/rg/apim-1"], "recommendations": []}

        # --- Act ---
        result_state = strategic_caching_analysis_node(initial_state)

        # --- Assert ---
        # Should generate 2 recommendations, one for each GET operation
        self.assertEqual(len(result_state["recommendations"]), 2)

        rec_types = [rec["type"] for rec in result_state["recommendations"]]
        self.assertTrue(all(t == "POLICY_ADD_CACHE" for t in rec_types))

        # Check that the PUT operation was ignored and not in the recommendations
        rec_op_ids = [rec["payload"]["operation_id"] for rec in result_state["recommendations"]]
        self.assertIn("get-user", rec_op_ids)
        self.assertIn("get-settings", rec_op_ids)
        self.assertNotIn("update-user", rec_op_ids)

    @patch('finops_agent.finops_agent.tools.azure.execute_kql_query')
    def test_no_recommendation_when_kql_returns_empty(self, mock_execute_kql):
        """
        Tests that no recommendations are generated when the KQL query returns no results.
        """
        # --- Arrange ---
        mock_execute_kql.return_value = []
        initial_state = {"resources": ["/sub/rg/apim-1"], "recommendations": []}

        # --- Act ---
        result_state = strategic_caching_analysis_node(initial_state)

        # --- Assert ---
        self.assertEqual(len(result_state["recommendations"]), 0)

    @patch('finops_agent.finops_agent.tools.azure.execute_kql_query')
    def test_handles_malformed_data_gracefully(self, mock_execute_kql):
        """
        Tests that the node handles rows with missing keys without crashing.
        """
        # --- Arrange ---
        mock_execute_kql.return_value = [
            {"OperationId": "good-op", "ApiId": "/apis/good-api", "RequestMethod": "GET"},
            {"ApiId": "/apis/bad-api-1", "RequestMethod": "GET"}, # Missing OperationId
            {"OperationId": "bad-op-2", "RequestMethod": "GET"}  # Missing ApiId
        ]
        initial_state = {"resources": ["/sub/rg/apim-1"], "recommendations": []}

        # --- Act ---
        result_state = strategic_caching_analysis_node(initial_state)

        # --- Assert ---
        # Should only generate 1 recommendation for the valid row
        self.assertEqual(len(result_state["recommendations"]), 1)
        self.assertEqual(result_state["recommendations"][0]["payload"]["operation_id"], "good-op")

if __name__ == '__main__':
    unittest.main()
