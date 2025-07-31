import datetime
from typing import Dict, Any, List

# Use a relative import to access the sibling 'tools' module.
from ...tools import azure

# Define constants for the analysis
UTILIZATION_THRESHOLD = 40.0  # P95 utilization percentage
METRICS_TIMEDELTA = datetime.timedelta(days=90)
METRIC_NAMES = ["Capacity"]  # Focusing on the main capacity metric for now

def tier_rightsizing_analysis_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes APIM instances for tier and SKU rightsizing opportunities by
    fetching properties and metrics and applying a set of rules.
    """
    print("---NODE: TIER RIGHTSIZING ANALYSIS (Live Logic)---")

    current_recommendations: List[Dict[str, Any]] = state.get("recommendations", [])
    resources_to_analyze: List[str] = state.get("resources", [])

    if not resources_to_analyze:
        print("No resources found to analyze.")
        return {"recommendations": current_recommendations}

    new_recommendations = []
    for resource_id in resources_to_analyze:
        print(f"Analyzing resource: {resource_id}")

        try:
            # 1. Get data from our tools
            properties = azure.get_apim_properties(resource_id)
            metrics = azure.get_apim_metrics(resource_id, METRIC_NAMES, METRICS_TIMEDELTA)

            sku_name = properties.get("sku", {}).get("name")
            p95_capacity = metrics.get("Capacity")
            instance_name = properties.get("name", "unknown")

            # 2. Implement analysis logic from Work Item 1

            # Rule 1: Sustained utilization below threshold
            if p95_capacity is not None and p95_capacity < UTILIZATION_THRESHOLD:
                rec = {
                    "id": f"REC-TR-{instance_name}",
                    "type": "TIER_CHANGE",
                    "resource_id": resource_id,
                    "details": f"Instance has a sustained 95th percentile Capacity of {p95_capacity}%, which is below the {UTILIZATION_THRESHOLD}% threshold. Recommending a SKU downgrade.",
                    "status": "pending_approval",
                    "source_node": "TierRightsizingAnalysisNode",
                    "payload": {
                        "current_sku": sku_name,
                        "p95_capacity": p95_capacity,
                        "recommended_action": "Downgrade SKU to a smaller size (e.g., from P2 to P1)."
                    }
                }
                new_recommendations.append(rec)
                print(f"  [+] Generated TIER_CHANGE recommendation for {resource_id}")

            # Rule 2: Premium instance with only VNet feature used
            is_vnet_enabled = properties.get("properties", {}).get("virtualNetworkType") != "None"
            is_multi_region = bool(properties.get("properties", {}).get("additionalLocations"))

            if sku_name == "Premium" and is_vnet_enabled and not is_multi_region:
                rec = {
                    "id": f"REC-PREM-VNET-{instance_name}",
                    "type": "TIER_CHANGE",
                    "resource_id": resource_id,
                    "details": "Instance is on the Premium tier with VNet enabled but is not multi-region. It is a candidate for downgrade to the Standard_v2 tier, which also supports VNet at a lower cost.",
                    "status": "pending_approval",
                    "source_node": "TierRightsizingAnalysisNode",
                    "payload": {
                        "current_sku": sku_name,
                        "recommended_sku": "Standard_v2"
                    }
                }
                new_recommendations.append(rec)
                print(f"  [+] Generated TIER_CHANGE (Premium to Standard_v2) recommendation for {resource_id}")

        except Exception as e:
            print(f"Could not analyze resource {resource_id}. Error: {e}")

    # Return the combined list of old and new recommendations
    return {"recommendations": current_recommendations + new_recommendations}
