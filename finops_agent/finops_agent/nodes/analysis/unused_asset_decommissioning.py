from typing import Dict, Any, List

from ...tools import azure

# --- Constants for Decommissioning Analysis ---
# The ID of the built-in Azure Policy that identifies APIs with no traffic in 30 days.
UNUSED_ENDPOINTS_POLICY_ID = "/providers/Microsoft.Authorization/policyDefinitions/c82362a3-b5c3-4b39-95c9-441a14a09c2d" # Example ID
LOG_ANALYTICS_WORKSPACE_ID = "placeholder_workspace_id"
DEEP_DIVE_TIMESPAN = "180d"

def _build_traffic_check_query(asset_id: str, timespan: str) -> str:
    """Builds the KQL query to check for any traffic to a specific asset."""
    query = f"""
    ApiManagementGatewayLogs
    | where TimeGenerated > ago({timespan})
    | where BackendId contains '{asset_id}' or FrontendId contains '{asset_id}'
    | count
    """
    return query.strip()

def _has_dependencies(asset_id: str) -> bool:
    """
    Simulates a dependency check for an asset.
    In a real implementation, this would query ARM to see if the asset is
    part of a Product, referenced in another API's policy, etc.
    """
    print(f"  - (Simulated) Checking dependencies for {asset_id}...")
    # For now, assume no dependencies are found.
    return False

def unused_asset_decommissioning_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes APIM assets to find unused APIs, operations, and products that can be decommissioned.
    """
    print("---NODE: UNUSED ASSET DECOMMISSIONING (Live Logic)---")

    current_recommendations: List[Dict[str, Any]] = state.get("recommendations", [])
    new_recommendations = []

    # 1. Get initial candidates from Azure Policy
    policy_candidates = azure.get_azure_policy_results(UNUSED_ENDPOINTS_POLICY_ID)
    print(f"Found {len(policy_candidates)} potential unused assets from Azure Policy.")

    for asset_id in policy_candidates:
        print(f"Analyzing candidate: {asset_id}")

        # 2. Run deep-dive KQL query to confirm zero traffic over a longer period
        kql_query = _build_traffic_check_query(asset_id, DEEP_DIVE_TIMESPAN)
        query_results = azure.execute_kql_query(LOG_ANALYTICS_WORKSPACE_ID, kql_query)

        request_count = query_results[0].get("RequestCount") if query_results else -1

        if request_count == 0:
            print(f"  - Confirmed zero traffic for {asset_id} over {DEEP_DIVE_TIMESPAN}.")

            # 3. Perform dependency check
            if not _has_dependencies(asset_id):
                print(f"  - No dependencies found for {asset_id}. Generating recommendation.")
                rec = {
                    "id": f"REC-DECOM-{asset_id.replace('/', '_')}",
                    "type": "DECOMMISSION_ASSET",
                    "resource_id": asset_id,
                    "details": f"Asset '{asset_id}' has had zero traffic for over {DEEP_DIVE_TIMESPAN} and has no detected dependencies. It is recommended for decommissioning.",
                    "status": "pending_approval",
                    "source_node": "UnusedAssetDecommissioningNode",
                    "payload": {
                        "asset_id": asset_id,
                        "verified_period_days": 180
                    }
                }
                new_recommendations.append(rec)
            else:
                print(f"  - Skipping {asset_id} due to detected dependencies.")
        else:
            print(f"  - Skipping {asset_id} due to traffic ({request_count} requests) found in the last {DEEP_DIVE_TIMESPAN}.")

    print(f"Generated {len(new_recommendations)} decommissioning recommendations.")
    return {"recommendations": current_recommendations + new_recommendations}
