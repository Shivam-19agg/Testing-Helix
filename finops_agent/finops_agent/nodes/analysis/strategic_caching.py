from typing import Dict, Any, List

from ...tools import azure

# --- Constants for Caching Analysis ---
# The Log Analytics Workspace ID would typically be discovered or configured.
LOG_ANALYTICS_WORKSPACE_ID = "placeholder_workspace_id"
TIME_AGO = "30d"
REQUEST_THRESHOLD = 1000
BACKEND_TIME_THRESHOLD = 0.25  # seconds
RECOMMENDED_CACHE_DURATION = 60  # seconds

def _build_kql_query(time_ago: str, request_threshold: int, backend_time_threshold: float) -> str:
    """Builds the KQL query to find caching candidates."""
    # This query finds the top 10 GET operations that are slower than the threshold
    # and have a request count higher than the threshold.
    query = f"""
    ApiManagementGatewayLogs
    | where TimeGenerated > ago({time_ago})
    | where RequestMethod == "GET"
    | where BackendResponseTime > {backend_time_threshold}
    | summarize RequestCount = count(), AvgBackendResponseTime = avg(BackendResponseTime) by ApiId, OperationId
    | where RequestCount > {request_threshold}
    | order by RequestCount desc
    | top 10 by RequestCount
    """
    return query.strip()

def strategic_caching_analysis_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes API gateway logs to find operations that would benefit from caching.
    """
    print("---NODE: STRATEGIC CACHING ANALYSIS (Live Logic)---")

    current_recommendations: List[Dict[str, Any]] = state.get("recommendations", [])
    new_recommendations = []

    # 1. Build the KQL query
    kql_query = _build_kql_query(TIME_AGO, REQUEST_THRESHOLD, BACKEND_TIME_THRESHOLD)

    # 2. Execute the query using our tool
    query_results = azure.execute_kql_query(LOG_ANALYTICS_WORKSPACE_ID, kql_query)

    if not query_results:
        print("No potential caching candidates found in logs.")
        return {"recommendations": current_recommendations}

    print(f"Found {len(query_results)} potential caching candidates from logs.")

    # 3. Process results and generate recommendations
    for row in query_results:
        api_id = row.get("ApiId")
        operation_id = row.get("OperationId")
        request_method = row.get("RequestMethod")

        # Defensive check: Only recommend caching for idempotent GET operations,
        # even though the KQL query should have already filtered.
        if request_method != "GET":
            print(f"  - Skipping operation '{operation_id}' ('{request_method}') from results as it's not a GET request.")
            continue

        if not api_id or not operation_id:
            continue

        rec = {
            "id": f"REC-CACHE-{api_id.replace('/', '_')}-{operation_id}",
            "type": "POLICY_ADD_CACHE",
            "resource_id": f"{api_id}/operations/{operation_id}",  # The resource is the specific API operation
            "details": f"Operation '{operation_id}' in API '{api_id}' is a good candidate for caching. "
                       f"It's a GET operation with a high request count ({row.get('RequestCount')}) "
                       f"and an average backend response time of {row.get('AvgBackendResponseTime', 0):.2f}s.",
            "status": "pending_approval",
            "source_node": "StrategicCachingAnalysisNode",
            "payload": {
                "api_id": api_id,
                "operation_id": operation_id,
                "recommended_cache_duration_seconds": RECOMMENDED_CACHE_DURATION
            }
        }
        new_recommendations.append(rec)

    print(f"Generated {len(new_recommendations)} caching recommendations.")
    return {"recommendations": current_recommendations + new_recommendations}
