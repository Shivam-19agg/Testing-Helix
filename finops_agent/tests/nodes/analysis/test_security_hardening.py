import unittest
from unittest.mock import patch

from finops_agent.finops_agent.nodes.analysis.security_hardening import security_hardening_node

class TestSecurityHardeningNode(unittest.TestCase):

    @patch('finops_agent.finops_agent.tools.azure.get_apim_properties')
    def test_insecure_instance_generates_recommendations(self, mock_get_properties):
        """
        Tests that an instance with multiple security issues generates a recommendation for each.
        """
        # --- Arrange ---
        mock_get_properties.return_value = {
            "name": "apim-insecure",
            "properties": {
                "publicIpAddressId": "/subscriptions/subid/resourceGroups/rg/providers/Microsoft.Network/publicIPAddresses/apim-insecure-pip",
                "customProperties": {
                    "Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Protocols.Tls10": "True",
                    "Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Ciphers.TripleDes168": "True"
                }
            }
        }
        initial_state = {"resources": ["/sub/apim-insecure"], "recommendations": []}

        # --- Act ---
        result_state = security_hardening_node(initial_state)

        # --- Assert ---
        # Expect 3 recommendations: 1 for public IP, 1 for TLS 1.0, 1 for Triple DES
        self.assertEqual(len(result_state["recommendations"]), 3)
        findings = [rec["payload"]["finding"] for rec in result_state["recommendations"]]
        self.assertIn("Public Management Endpoint", findings)
        self.assertIn("Weak TLS Protocol", findings)
        self.assertIn("Weak Cipher", findings)

    @patch('finops_agent.finops_agent.tools.azure.get_apim_properties')
    def test_secure_instance_generates_no_recommendations(self, mock_get_properties):
        """
        Tests that a secure instance generates no recommendations.
        """
        # --- Arrange ---
        mock_get_properties.return_value = {
            "name": "apim-secure",
            "properties": {
                "publicIpAddressId": None,
                "customProperties": {
                    "Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Protocols.Tls10": "False",
                    "Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Ciphers.TripleDes168": "False"
                }
            }
        }
        initial_state = {"resources": ["/sub/apim-secure"], "recommendations": []}

        # --- Act ---
        result_state = security_hardening_node(initial_state)

        # --- Assert ---
        self.assertEqual(len(result_state["recommendations"]), 0)

    @patch('finops_agent.finops_agent.tools.azure.get_apim_properties')
    def test_graceful_handling_of_missing_custom_properties(self, mock_get_properties):
        """
        Tests that the node runs without error if the customProperties key is missing.
        """
        # --- Arrange ---
        mock_get_properties.return_value = {
            "name": "apim-no-custom-props",
            "properties": {
                "publicIpAddressId": None,
                # customProperties key is missing
            }
        }
        initial_state = {"resources": ["/sub/apim-no-custom-props"], "recommendations": []}

        # --- Act ---
        result_state = security_hardening_node(initial_state)

        # --- Assert ---
        # No recommendations should be generated, and no crash should occur.
        self.assertEqual(len(result_state["recommendations"]), 0)

if __name__ == '__main__':
    unittest.main()
