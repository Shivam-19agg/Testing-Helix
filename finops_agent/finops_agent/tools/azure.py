import datetime
from typing import Dict, Any, List

# Note: The actual implementation of these functions will require authentication
# to Azure. This is often handled by `azure.identity.DefaultAzureCredential`.
# For now, these functions are placeholders that define the interface
# and return mock data, allowing the analysis node to be developed independently.

def get_apim_properties(resource_id: str) -> Dict[str, Any]:
    """
    Fetches the properties of an Azure API Management instance.

    In a real implementation, this would use the azure-mgmt-apimanagement client.

    Args:
        resource_id: The full resource ID of the APIM instance.

    Returns:
        A dictionary containing key properties like SKU name, VNet status, etc.
    """
    print(f"---AZURE TOOL (MOCK): Fetching properties for {resource_id}---")

    # This mock data simulates different types of APIM instances.
    if "apim-prod-eus" in resource_id:
        # Simulates an overprovisioned Premium instance with some insecure settings
        return {
            "name": "apim-prod-eus",
            "sku": {"name": "Premium", "capacity": 2},
            "properties": {
                "virtualNetworkType": "External",
                "additionalLocations": [],
                "publicIpAddressId": "/subscriptions/subid/resourceGroups/rg/providers/Microsoft.Network/publicIPAddresses/apim-prod-eus-pip", # Public IP indicates public management endpoint
                "customProperties": {
                    "Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Protocols.Tls10": "True", # Insecure
                    "Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Protocols.Tls11": "True", # Insecure
                    "Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Ciphers.TripleDes168": "True" # Insecure
                }
            }
        }
    elif "apim-dev-wus" in resource_id:
        # Simulates a more secure Developer instance
         return {
            "name": "apim-dev-wus",
            "sku": {"name": "Developer", "capacity": 1},
            "properties": {
                "virtualNetworkType": "None",
                "additionalLocations": [],
                "publicIpAddressId": None, # No public management endpoint
                "customProperties": {
                    "Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Protocols.Tls10": "False",
                    "Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Protocols.Tls11": "False",
                    "Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Ciphers.TripleDes168": "False"
                }
            }
        }
    else:
        # Default mock response
        return {
            "name": "default-apim",
            "sku": {"name": "Basic", "capacity": 1},
            "properties": {
                "virtualNetworkType": "None",
                "additionalLocations": []
            }
        }

def get_apim_metrics(resource_id: str, metric_names: List[str], timespan: datetime.timedelta) -> Dict[str, float]:
    """
    Fetches the 95th percentile metrics for an APIM instance over a specified timespan.

    In a real implementation, this would use the azure-mgmt-monitor client.

    Args:
        resource_id: The full resource ID of the APIM instance.
        metric_names: A list of metric names to fetch (e.g., 'Capacity', 'CpuPercentage').
        timespan: The duration over which to fetch the metrics.

    Returns:
        A dictionary mapping metric names to their P95 values.
    """
    print(f"---AZURE TOOL (MOCK): Fetching {metric_names} for {resource_id} over past {timespan}---")

    # This mock data simulates low utilization for the production instance.
    if "apim-prod-eus" in resource_id:
        return {
            "Capacity": 22.5,          # P95 Capacity is well below the threshold of 40%
            "CpuPercentage": 15.0,
            "MemoryPercentage": 25.0,
            "Requests": 120000.0
        }
    else:
        # Default metrics for other instances
        return {
            "Capacity": 60.0,
            "CpuPercentage": 55.0,
            "MemoryPercentage": 65.0,
            "Requests": 5000000.0
        }

def list_all_apim_instances(subscription_id: str) -> List[Dict[str, Any]]:
    """
    Lists all APIM instances in a given subscription.

    In a real implementation, this would use the azure-mgmt-apimanagement client
    to list all services across all resource groups.

    Args:
        subscription_id: The ID of the subscription to scan.

    Returns:
        A list of dictionaries, where each dictionary is the full resource object
        of an APIM instance.
    """
    print(f"---AZURE TOOL (MOCK): Listing all APIM instances in subscription {subscription_id}---")

    # This mock data simulates a scenario with instance sprawl, where multiple
    # underutilized instances exist that could be candidates for consolidation.
    return [
        {
            "id": f"/subscriptions/{subscription_id}/resourceGroups/rg-prod-1/providers/Microsoft.ApiManagement/service/apim-prod-eus",
            "name": "apim-prod-eus",
            "sku": {"name": "Premium", "capacity": 2},
            "properties": {
                "virtualNetworkType": "External",
                "additionalLocations": []
            }
        },
        {
            "id": f"/subscriptions/{subscription_id}/resourceGroups/rg-dev-1/providers/Microsoft.ApiManagement/service/apim-dev-wus",
            "name": "apim-dev-wus",
            "sku": {"name": "Developer", "capacity": 1},
            "properties": {
                "virtualNetworkType": "None",
                "additionalLocations": []
            }
        },
        {
            "id": f"/subscriptions/{subscription_id}/resourceGroups/rg-staging-1/providers/Microsoft.ApiManagement/service/apim-staging-eus",
            "name": "apim-staging-eus",
            "sku": {"name": "Basic", "capacity": 1},
            "properties": {
                "virtualNetworkType": "None",
                "additionalLocations": []
            }
        },
        {
            "id": f"/subscriptions/{subscription_id}/resourceGroups/rg-legacy-1/providers/Microsoft.ApiManagement/service/apim-legacy-wus",
            "name": "apim-legacy-wus",
            "sku": {"name": "Basic", "capacity": 1},
            "properties": {
                "virtualNetworkType": "None",
                "additionalLocations": []
            }
        }
    ]

def execute_kql_query(workspace_id: str, query: str) -> List[Dict[str, Any]]:
    """
    Executes a Kusto Query Language (KQL) query against a Log Analytics workspace.

    In a real implementation, this would use the azure-kusto-data client to
    connect to the workspace and execute the query.

    Args:
        workspace_id: The resource ID of the Log Analytics workspace.
        query: The KQL query string to execute.

    Returns:
        A list of dictionaries representing the rows of the query result.
    """
    print(f"---AZURE TOOL (MOCK): Executing KQL query in workspace {workspace_id}---")
    print(f"Query: {query}")

    # This mock data simulates a typical result from querying ApiManagementGatewayLogs
    # for high-traffic, slow GET operations.
    if "ApiManagementGatewayLogs" in query and "summarize" in query:
        return [
            {
                "OperationId": "get-profile",
                "ApiId": "/apis/user-profile-api",
                "RequestMethod": "GET",
                "RequestCount": 58230,
                "AvgBackendResponseTime": 0.35  # seconds
            },
            {
                "OperationId": "list-products",
                "ApiId": "/apis/product-catalog-api",
                "RequestMethod": "GET",
                "RequestCount": 102401,
                "AvgBackendResponseTime": 0.55  # seconds
            },
            {
                "OperationId": "create-profile",
                "ApiId": "/apis/user-profile-api",
                "RequestMethod": "POST",  # Should be ignored by the caching logic
                "RequestCount": 1500,
                "AvgBackendResponseTime": 0.20
            }
        ]
    elif "ApiManagementGatewayLogs" in query and "count" in query:
        # This simulates the deep-dive query to confirm zero traffic for a specific asset.
        if "old-legacy-api" in query or "get-user-v1" in query:
            # These are truly abandoned.
            return [{"RequestCount": 0}]
        elif "product-api" in query:
            # This one had a burst of traffic recently, so it's not abandoned.
            return [{"RequestCount": 5}]
        else:
            return [{"RequestCount": 100}] # Default for other assets

    return []

def get_azure_policy_results(policy_definition_id: str) -> List[str]:
    """
    Simulates fetching results from an Azure Policy assignment.

    Args:
        policy_definition_id: The definition ID of the policy to query.

    Returns:
        A list of resource IDs for non-compliant resources.
    """
    print(f"---AZURE TOOL (MOCK): Fetching Azure Policy results for {policy_definition_id}---")

    # Check if it's the policy we care about for this node
    if "c82362a3-b5c3-4b39-95c9-441a14a09c2d" in policy_definition_id:
        # These are the assets initially flagged by the policy as having no traffic
        # in the last 30 days. The analysis node will then verify this over a longer period.
        return [
            "/subscriptions/subid/resourceGroups/rg/providers/Microsoft.ApiManagement/service/apim1/apis/old-legacy-api",
            "/subscriptions/subid/resourceGroups/rg/providers/Microsoft.ApiManagement/service/apim1/apis/user-api/operations/get-user-v1", # An old version of an operation
            "/subscriptions/subid/resourceGroups/rg/providers/Microsoft.ApiManagement/service/apim1/apis/product-api" # This one will have recent traffic in our deep-dive query
        ]
    return []

def list_apis(apim_instance_id: str) -> List[Dict[str, Any]]:
    """Simulates listing the APIs for a given APIM instance."""
    print(f"---AZURE TOOL (MOCK): Listing APIs for instance {apim_instance_id}---")
    return [
        {"id": f"{apim_instance_id}/apis/echo-api", "name": "Echo API"},
        {"id": f"{apim_instance_id}/apis/user-api", "name": "User API"},
    ]

def list_products(apim_instance_id: str) -> List[Dict[str, Any]]:
    """Simulates listing the Products for a given APIM instance."""
    print(f"---AZURE TOOL (MOCK): Listing Products for instance {apim_instance_id}---")
    return [
        {"id": f"{apim_instance_id}/products/starter", "name": "Starter"},
        {"id": f"{apim_instance_id}/products/unlimited", "name": "Unlimited"},
    ]

def get_apim_policy_xml(asset_id: str) -> str:
    """
    Simulates fetching the policy XML for an APIM asset (API or Product).
    """
    print(f"---AZURE TOOL (MOCK): Fetching policy XML for {asset_id}---")
    # Return a policy that is missing a rate limit for the 'user-api'
    if "apis/user-api" in asset_id:
        return """
<policies>
    <inbound>
        <base />
        <set-header name="X-Request-Context-Data" exists-action="override">
            <value>@(context.Deployment.Region)</value>
        </set-header>
    </inbound>
    <backend>
        <base />
    </backend>
    <outbound>
        <base />
    </outbound>
    <on-error>
        <base />
    </on-error>
</policies>
"""
    # Return a policy that includes a rate limit for all other assets
    else:
        return """
<policies>
    <inbound>
        <rate-limit-by-key calls="10" renewal-period="60" counter-key="@(context.Subscription.Id)" />
        <base />
    </inbound>
    <backend>
        <base />
    </backend>
    <outbound>
        <base />
    </outbound>
    <on-error>
        <base />
    </on-error>
</policies>
"""
