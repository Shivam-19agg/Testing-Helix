import unittest
from unittest.mock import patch, MagicMock

# The function we want to test
from finops_agent.finops_agent.nodes.analysis.tier_rightsizing import tier_rightsizing_analysis_node

class TestTierRightsizingAnalysisNode(unittest.TestCase):

    # Use patch to replace the real azure tool functions with mocks during the tests
    @patch('finops_agent.finops_agent.tools.azure.get_apim_metrics')
    @patch('finops_agent.finops_agent.tools.azure.get_apim_properties')
    def test_underutilized_and_premium_vnet_instance(self, mock_get_properties, mock_get_metrics):
        """
        Tests that an underutilized Premium instance with VNet generates two separate recommendations.
        """
        # --- Arrange ---
        # Configure the mock return values for our Azure tool functions
        mock_get_properties.return_value = {
            "name": "apim-test-prod",
            "sku": {"name": "Premium", "capacity": 1},
            "properties": {
                "virtualNetworkType": "External", # VNet is enabled
                "additionalLocations": [] # Multi-region is disabled
            }
        }
        mock_get_metrics.return_value = {
            "Capacity": 20.0 # P95 capacity is below the 40% threshold
        }

        # Define the initial state for the test
        initial_state = {
            "resources": ["/subscriptions/subid/resourceGroups/rg/providers/Microsoft.ApiManagement/service/apim-test-prod"],
            "recommendations": []
        }

        # --- Act ---
        # Call the node function with the test state
        result_state = tier_rightsizing_analysis_node(initial_state)

        # --- Assert ---
        # Check that two recommendations were generated
        self.assertEqual(len(result_state["recommendations"]), 2)

        # Check the details of the first recommendation (underutilization)
        rec1 = result_state["recommendations"][0]
        self.assertEqual(rec1["type"], "TIER_CHANGE")
        self.assertIn("sustained 95th percentile Capacity of 20.0%", rec1["details"])

        # Check the details of the second recommendation (Premium to Standard_v2)
        rec2 = result_state["recommendations"][1]
        self.assertEqual(rec2["type"], "TIER_CHANGE")
        self.assertEqual(rec2["payload"]["recommended_sku"], "Standard_v2")

    @patch('finops_agent.finops_agent.tools.azure.get_apim_metrics')
    @patch('finops_agent.finops_agent.tools.azure.get_apim_properties')
    def test_healthy_instance(self, mock_get_properties, mock_get_metrics):
        """
        Tests that a healthy instance with high utilization does not generate a recommendation.
        """
        # --- Arrange ---
        mock_get_properties.return_value = {
            "name": "apim-healthy",
            "sku": {"name": "Standard", "capacity": 1},
            "properties": {"virtualNetworkType": "None", "additionalLocations": []}
        }
        mock_get_metrics.return_value = {
            "Capacity": 85.0 # High utilization
        }
        initial_state = {"resources": ["/subscriptions/subid/resourceGroups/rg/providers/Microsoft.ApiManagement/service/apim-healthy"], "recommendations": []}

        # --- Act ---
        result_state = tier_rightsizing_analysis_node(initial_state)

        # --- Assert ---
        self.assertEqual(len(result_state["recommendations"]), 0)

    def test_no_resources(self):
        """
        Tests that the node runs correctly when there are no resources to analyze.
        """
        # --- Arrange ---
        initial_state = {"resources": [], "recommendations": []}

        # --- Act ---
        result_state = tier_rightsizing_analysis_node(initial_state)

        # --- Assert ---
        self.assertEqual(len(result_state["recommendations"]), 0)

if __name__ == '__main__':
    unittest.main()
