import unittest
from unittest.mock import patch

from finops_agent.finops_agent.nodes.analysis.rate_limit_policy import throttling_policy_enforcement_node

class TestThrottlingPolicyEnforcementNode(unittest.TestCase):

    @patch('finops_agent.finops_agent.tools.azure.get_apim_policy_xml')
    @patch('finops_agent.finops_agent.tools.azure.list_products')
    @patch('finops_agent.finops_agent.tools.azure.list_apis')
    @patch('finops_agent.finops_agent.tools.azure.list_all_apim_instances')
    def test_recommendation_when_policy_is_missing(self, mock_list_instances, mock_list_apis, mock_list_products, mock_get_policy):
        """
        Tests that a recommendation is generated when a rate-limit policy is missing.
        """
        # --- Arrange ---
        mock_list_instances.return_value = [{"id": "/sub/apim1", "name": "apim1"}]
        mock_list_apis.return_value = [{"id": "/sub/apim1/apis/api1", "name": "api1"}]
        mock_list_products.return_value = []
        # Mock a policy XML that has no rate-limit or quota-by-key elements
        mock_get_policy.return_value = "<policies><inbound><base /></inbound></policies>"

        initial_state = {"resources": ["/sub/apim1"], "recommendations": []}

        # --- Act ---
        result_state = throttling_policy_enforcement_node(initial_state)

        # --- Assert ---
        self.assertEqual(len(result_state["recommendations"]), 1)
        self.assertEqual(result_state["recommendations"][0]["type"], "POLICY_ADD_RATELIMIT")

    @patch('finops_agent.finops_agent.tools.azure.get_apim_policy_xml')
    @patch('finops_agent.finops_agent.tools.azure.list_products')
    @patch('finops_agent.finops_agent.tools.azure.list_apis')
    @patch('finops_agent.finops_agent.tools.azure.list_all_apim_instances')
    def test_no_recommendation_when_rate_limit_exists(self, mock_list_instances, mock_list_apis, mock_list_products, mock_get_policy):
        """
        Tests that no recommendation is generated when a <rate-limit-by-key> policy exists.
        """
        # --- Arrange ---
        mock_list_instances.return_value = [{"id": "/sub/apim1", "name": "apim1"}]
        mock_list_apis.return_value = [{"id": "/sub/apim1/apis/api1", "name": "api1"}]
        mock_list_products.return_value = []
        mock_get_policy.return_value = "<policies><inbound><rate-limit-by-key calls='10' renewal-period='60' /></inbound></policies>"
        initial_state = {"resources": ["/sub/apim1"], "recommendations": []}

        # --- Act ---
        result_state = throttling_policy_enforcement_node(initial_state)

        # --- Assert ---
        self.assertEqual(len(result_state["recommendations"]), 0)

    @patch('finops_agent.finops_agent.tools.azure.get_apim_policy_xml')
    @patch('finops_agent.finops_agent.tools.azure.list_products')
    @patch('finops_agent.finops_agent.tools.azure.list_apis')
    @patch('finops_agent.finops_agent.tools.azure.list_all_apim_instances')
    def test_no_recommendation_when_quota_exists(self, mock_list_instances, mock_list_apis, mock_list_products, mock_get_policy):
        """
        Tests that no recommendation is generated when a <quota-by-key> policy exists.
        """
        # --- Arrange ---
        mock_list_instances.return_value = [{"id": "/sub/apim1", "name": "apim1"}]
        mock_list_apis.return_value = []
        mock_list_products.return_value = [{"id": "/sub/apim1/products/prod1", "name": "prod1"}]
        mock_get_policy.return_value = "<policies><inbound><quota-by-key calls='1000' bandwidth='1024' renewal-period='3600' /></inbound></policies>"
        initial_state = {"resources": ["/sub/apim1"], "recommendations": []}

        # --- Act ---
        result_state = throttling_policy_enforcement_node(initial_state)

        # --- Assert ---
        self.assertEqual(len(result_state["recommendations"]), 0)

    @patch('finops_agent.finops_agent.tools.azure.get_apim_policy_xml')
    @patch('finops_agent.finops_agent.tools.azure.list_products')
    @patch('finops_agent.finops_agent.tools.azure.list_apis')
    @patch('finops_agent.finops_agent.tools.azure.list_all_apim_instances')
    def test_graceful_handling_of_malformed_xml(self, mock_list_instances, mock_list_apis, mock_list_products, mock_get_policy):
        """
        Tests that the node handles malformed XML without crashing.
        """
        # --- Arrange ---
        mock_list_instances.return_value = [{"id": "/sub/apim1", "name": "apim1"}]
        mock_list_apis.return_value = [{"id": "/sub/apim1/apis/api1", "name": "api1"}]
        mock_list_products.return_value = []
        mock_get_policy.return_value = "<policies><inbound>" # Malformed XML
        initial_state = {"resources": ["/sub/apim1"], "recommendations": []}

        # --- Act ---
        result_state = throttling_policy_enforcement_node(initial_state)

        # --- Assert ---
        # No recommendation should be made for a policy that can't be parsed,
        # as we can't be certain a rate-limit doesn't exist.
        self.assertEqual(len(result_state["recommendations"]), 0)


if __name__ == '__main__':
    unittest.main()
