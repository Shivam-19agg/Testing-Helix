from typing import Dict, Any, List, Optional
from lxml import etree

from ...tools import azure

def _policy_has_rate_limit(policy_xml: str) -> Optional[bool]:
    """
    Parses policy XML and checks for the existence of rate-limiting policies.
    Returns True if a rate-limit policy is found.
    Returns False if no rate-limit policy is found.
    Returns None if the policy XML is malformed or empty.
    """
    if not policy_xml.strip():
        return None

    try:
        # The fromstring function requires bytes, so we encode the string
        root = etree.fromstring(policy_xml.encode('utf-8'))

        # Use XPath to find the rate-limit or quota elements within the inbound section
        rate_limit = root.xpath('//inbound/rate-limit-by-key')
        quota = root.xpath('//inbound/quota-by-key')

        return bool(rate_limit) or bool(quota)
    except etree.XMLSyntaxError:
        # Handle cases where the policy XML is malformed
        print(f"Warning: Could not parse policy XML.")
        return None


def throttling_policy_enforcement_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Audits APIs and Products to ensure they are protected by rate-limiting policies.
    """
    print("---NODE: THROTTLING POLICY ENFORCEMENT (Live Logic)---")

    current_recommendations: List[Dict[str, Any]] = state.get("recommendations", [])
    new_recommendations = []

    # This node needs a subscription ID. We'll extract it from the first resource ID.
    if not state.get("resources"):
        print("No resources found, cannot determine subscription ID.")
        return {"recommendations": current_recommendations}

    first_resource_id = state["resources"][0]
    subscription_id = first_resource_id.split('/')[2]

    # 1. Get all APIM instances
    all_instances = azure.list_all_apim_instances(subscription_id)

    for instance in all_instances:
        instance_id = instance["id"]
        print(f"Analyzing instance: {instance['name']}")

        # 2. Get all APIs and Products for the instance
        apis = azure.list_apis(instance_id)
        products = azure.list_products(instance_id)
        assets_to_check = apis + products

        # 3. Check the policy for each asset
        for asset in assets_to_check:
            asset_id = asset["id"]
            policy_xml = azure.get_apim_policy_xml(asset_id)
            has_limit = _policy_has_rate_limit(policy_xml)

            # Only generate a recommendation if we can be certain there is no policy.
            # If has_limit is None, the policy was unparseable, so we skip it.
            if has_limit is False:
                print(f"  - No rate limit found for asset: {asset['name']}")
                rec = {
                    "id": f"REC-RATELIMIT-{asset_id.replace('/', '_')}",
                    "type": "POLICY_ADD_RATELIMIT",
                    "resource_id": asset_id,
                    "details": f"The asset '{asset['name']}' is not protected by a rate-limit or quota policy. Adding one can prevent abuse and protect backend services.",
                    "status": "pending_approval",
                    "source_node": "ThrottlingPolicyEnforcementNode",
                    "payload": {
                        "asset_id": asset_id,
                        "asset_type": "API" if "/apis/" in asset_id else "Product"
                    }
                }
                new_recommendations.append(rec)

    print(f"Generated {len(new_recommendations)} rate-limiting recommendations.")
    return {"recommendations": current_recommendations + new_recommendations}
