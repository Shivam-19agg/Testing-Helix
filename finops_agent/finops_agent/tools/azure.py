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
        # Simulates an overprovisioned Premium instance
        return {
            "name": "apim-prod-eus",
            "sku": {"name": "Premium", "capacity": 2},
            "properties": {
                "virtualNetworkType": "External", # VNet enabled
                "additionalLocations": [] # Not multi-region
            }
        }
    elif "apim-dev-wus" in resource_id:
        # Simulates a correctly provisioned Developer instance
         return {
            "name": "apim-dev-wus",
            "sku": {"name": "Developer", "capacity": 1},
            "properties": {
                "virtualNetworkType": "None",
                "additionalLocations": []
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
