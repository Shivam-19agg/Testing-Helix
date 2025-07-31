import datetime
from typing import Dict, Any, List

from ...tools import azure

# --- Constants for Consolidation Analysis ---
# We will only consider consolidating Basic and Standard instances.
# Premium has unique features, and Developer is not for production use.
ELIGIBLE_SKUS_FOR_CONSOLIDATION = ["Basic", "Standard"]
# An instance is considered underutilized if its P95 capacity is below this percentage.
CAPACITY_THRESHOLD = 30.0
METRICS_TIMEDELTA = datetime.timedelta(days=90)
METRIC_NAMES = ["Capacity"]

def _calculate_complexity(instance_count: int) -> str:
    """Calculates a simple migration complexity score."""
    if instance_count <= 3:
        return "Low"
    elif instance_count <= 5:
        return "Medium"
    else:
        return "High"

def instance_consolidation_analysis_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes all APIM instances in a subscription to find consolidation opportunities.
    """
    print("---NODE: INSTANCE CONSOLIDATION ANALYSIS (Live Logic)---")

    current_recommendations: List[Dict[str, Any]] = state.get("recommendations", [])
    # This node needs a subscription ID to list all instances.
    # We'll extract it from the first resource ID found by the discovery node.
    # A more robust solution would pass the subscription ID in the state directly.
    if not state.get("resources"):
        print("No resources found, cannot determine subscription ID.")
        return {"recommendations": current_recommendations}

    first_resource_id = state["resources"][0]
    subscription_id = first_resource_id.split('/')[2]

    print(f"Scanning subscription {subscription_id} for consolidation candidates...")
    all_instances = azure.list_all_apim_instances(subscription_id)

    consolidation_candidates = []
    for instance in all_instances:
        instance_id = instance["id"]
        sku_name = instance.get("sku", {}).get("name")

        # Rule 1: Is the SKU eligible for consolidation?
        if sku_name not in ELIGIBLE_SKUS_FOR_CONSOLIDATION:
            print(f"  - Skipping instance {instance['name']} (SKU: {sku_name}) - not eligible.")
            continue

        # Rule 2: Is the instance underutilized?
        metrics = azure.get_apim_metrics(instance_id, METRIC_NAMES, METRICS_TIMEDELTA)
        p95_capacity = metrics.get("Capacity")

        if p95_capacity is not None and p95_capacity < CAPACITY_THRESHOLD:
            print(f"  - Found candidate: {instance['name']} (P95 Capacity: {p95_capacity}%)")
            consolidation_candidates.append(instance)
        else:
            print(f"  - Skipping instance {instance['name']} (P95 Capacity: {p95_capacity}%) - not underutilized.")

    # Rule 3: Do we have enough candidates to consolidate?
    if len(consolidation_candidates) >= 2:
        print(f"Found {len(consolidation_candidates)} instances to consolidate. Generating recommendation.")

        candidate_ids = [c["id"] for c in consolidation_candidates]
        total_capacity_needed = sum(azure.get_apim_metrics(c["id"], METRIC_NAMES, METRICS_TIMEDELTA).get("Capacity", 0) for c in consolidation_candidates)

        rec = {
            "id": f"REC-CONSOLIDATE-{subscription_id}",
            "type": "INSTANCE_CONSOLIDATE",
            "resource_id": subscription_id, # Recommendation applies to the whole subscription
            "details": f"Found {len(consolidation_candidates)} underutilized instances that can be consolidated into a single, right-sized instance.",
            "status": "pending_approval",
            "source_node": "InstanceConsolidationAnalysisNode",
            "payload": {
                "candidate_instances": candidate_ids,
                "estimated_capacity_for_new_instance": f"{total_capacity_needed:.2f}%",
                "migration_complexity_score": _calculate_complexity(len(consolidation_candidates))
            }
        }
        return {"recommendations": current_recommendations + [rec]}

    print("Fewer than 2 consolidation candidates found. No recommendation generated.")
    return {"recommendations": current_recommendations}
