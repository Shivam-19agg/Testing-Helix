import unittest
from unittest.mock import patch

from finops_agent.finops_agent.nodes.analysis.instance_consolidation import instance_consolidation_analysis_node

class TestInstanceConsolidationAnalysisNode(unittest.TestCase):

    @patch('finops_agent.finops_agent.tools.azure.get_apim_metrics')
    @patch('finops_agent.finops_agent.tools.azure.list_all_apim_instances')
    def test_consolidation_recommendation_success(self, mock_list_instances, mock_get_metrics):
        """
        Tests that a consolidation recommendation is generated when multiple
        underutilized, eligible instances are found.
        """
        # --- Arrange ---
        # Mock the list of all instances returned by the tool
        mock_list_instances.return_value = [
            {"id": "/sub/rg/apim-1", "name": "apim-1", "sku": {"name": "Basic"}},
            {"id": "/sub/rg/apim-2", "name": "apim-2", "sku": {"name": "Standard"}},
            {"id": "/sub/rg/apim-3", "name": "apim-3", "sku": {"name": "Premium"}}, # Ineligible SKU
            {"id": "/sub/rg/apim-4", "name": "apim-4", "sku": {"name": "Basic"}}, # Healthy
        ]

        # Mock the metrics for each instance. Use side_effect for different return values.
        mock_get_metrics.side_effect = [
            {"Capacity": 15.0}, # apim-1 is underutilized
            {"Capacity": 25.0}, # apim-2 is underutilized
            # No metrics call for apim-3 as it's skipped by SKU
            {"Capacity": 70.0}, # apim-4 is healthy
            # Metrics are fetched again when calculating total capacity
            {"Capacity": 15.0},
            {"Capacity": 25.0},
        ]

        initial_state = {
            "resources": ["/sub/rg/apim-1"], # Needed to get subscription ID
            "recommendations": []
        }

        # --- Act ---
        result_state = instance_consolidation_analysis_node(initial_state)

        # --- Assert ---
        self.assertEqual(len(result_state["recommendations"]), 1)
        rec = result_state["recommendations"][0]
        self.assertEqual(rec["type"], "INSTANCE_CONSOLIDATE")
        self.assertEqual(len(rec["payload"]["candidate_instances"]), 2)
        self.assertIn("/sub/rg/apim-1", rec["payload"]["candidate_instances"])
        self.assertIn("/sub/rg/apim-2", rec["payload"]["candidate_instances"])
        self.assertEqual(rec["payload"]["migration_complexity_score"], "Low")
        self.assertEqual(rec["payload"]["estimated_capacity_for_new_instance"], "40.00%")

    @patch('finops_agent.finops_agent.tools.azure.get_apim_metrics')
    @patch('finops_agent.finops_agent.tools.azure.list_all_apim_instances')
    def test_no_recommendation_due_to_lack_of_candidates(self, mock_list_instances, mock_get_metrics):
        """
        Tests that no recommendation is generated if fewer than two candidates are found.
        """
        # --- Arrange ---
        mock_list_instances.return_value = [
            {"id": "/sub/rg/apim-1", "name": "apim-1", "sku": {"name": "Basic"}},
            {"id": "/sub/rg/apim-2", "name": "apim-2", "sku": {"name": "Standard"}},
        ]
        mock_get_metrics.side_effect = [
            {"Capacity": 15.0}, # apim-1 is underutilized
            {"Capacity": 80.0}, # apim-2 is healthy
        ]
        initial_state = {"resources": ["/sub/rg/apim-1"], "recommendations": []}

        # --- Act ---
        result_state = instance_consolidation_analysis_node(initial_state)

        # --- Assert ---
        self.assertEqual(len(result_state["recommendations"]), 0)

if __name__ == '__main__':
    unittest.main()
