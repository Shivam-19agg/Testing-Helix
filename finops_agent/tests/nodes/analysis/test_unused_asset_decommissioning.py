import unittest
from unittest.mock import patch

from finops_agent.finops_agent.nodes.analysis.unused_asset_decommissioning import unused_asset_decommissioning_node

class TestUnusedAssetDecommissioningNode(unittest.TestCase):

    @patch('finops_agent.finops_agent.nodes.analysis.unused_asset_decommissioning._has_dependencies', return_value=False)
    @patch('finops_agent.finops_agent.tools.azure.execute_kql_query')
    @patch('finops_agent.finops_agent.tools.azure.get_azure_policy_results')
    def test_decommission_recommendation_success(self, mock_get_policy_results, mock_execute_kql, mock_has_dependencies):
        """
        Tests a successful scenario where an unused asset is identified and recommended for decommissioning.
        """
        # --- Arrange ---
        asset_id = "/apis/old-api"
        mock_get_policy_results.return_value = [asset_id]
        mock_execute_kql.return_value = [{"RequestCount": 0}] # Confirms zero traffic

        initial_state = {"resources": ["/subscriptions/subid/rg/apim1"], "recommendations": []}

        # --- Act ---
        result_state = unused_asset_decommissioning_node(initial_state)

        # --- Assert ---
        self.assertEqual(len(result_state["recommendations"]), 1)
        rec = result_state["recommendations"][0]
        self.assertEqual(rec["type"], "DECOMMISSION_ASSET")
        self.assertEqual(rec["resource_id"], asset_id)
        mock_has_dependencies.assert_called_once_with(asset_id)

    @patch('finops_agent.finops_agent.tools.azure.execute_kql_query')
    @patch('finops_agent.finops_agent.tools.azure.get_azure_policy_results')
    def test_no_recommendation_if_traffic_found_in_deep_dive(self, mock_get_policy_results, mock_execute_kql):
        """
        Tests that no recommendation is made if the KQL deep-dive finds recent traffic.
        """
        # --- Arrange ---
        asset_id = "/apis/active-api"
        mock_get_policy_results.return_value = [asset_id]
        mock_execute_kql.return_value = [{"RequestCount": 10}] # Traffic found
        initial_state = {"resources": ["/subscriptions/subid/rg/apim1"], "recommendations": []}

        # --- Act ---
        result_state = unused_asset_decommissioning_node(initial_state)

        # --- Assert ---
        self.assertEqual(len(result_state["recommendations"]), 0)

    @patch('finops_agent.finops_agent.nodes.analysis.unused_asset_decommissioning._has_dependencies', return_value=True)
    @patch('finops_agent.finops_agent.tools.azure.execute_kql_query')
    @patch('finops_agent.finops_agent.tools.azure.get_azure_policy_results')
    def test_no_recommendation_if_dependencies_found(self, mock_get_policy_results, mock_execute_kql, mock_has_dependencies):
        """
        Tests that no recommendation is made if the asset has dependencies, even with zero traffic.
        """
        # --- Arrange ---
        asset_id = "/apis/critical-api"
        mock_get_policy_results.return_value = [asset_id]
        mock_execute_kql.return_value = [{"RequestCount": 0}]
        initial_state = {"resources": ["/subscriptions/subid/rg/apim1"], "recommendations": []}

        # --- Act ---
        result_state = unused_asset_decommissioning_node(initial_state)

        # --- Assert ---
        self.assertEqual(len(result_state["recommendations"]), 0)
        mock_has_dependencies.assert_called_once_with(asset_id)

if __name__ == '__main__':
    unittest.main()
