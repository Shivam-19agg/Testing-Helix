from typing import Dict, Any, List

from ...tools import azure

# Define the insecure properties we are looking for.
# The key is the property name in the ARM response, and the value is the reason it's insecure.
INSECURE_PROTOCOLS = {
    "Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Protocols.Tls10": "TLS 1.0 is outdated and has known vulnerabilities.",
    "Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Protocols.Tls11": "TLS 1.1 is outdated and has known vulnerabilities.",
}
INSECURE_CIPHERS = {
    "Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Ciphers.TripleDes168": "Triple DES is a weak cipher and should be disabled."
}

def security_hardening_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Audits APIM instances against security best practices like TLS versions,
    cipher suites, and public endpoint exposure.
    """
    print("---NODE: SECURITY HARDENING (Live Logic)---")

    current_recommendations: List[Dict[str, Any]] = state.get("recommendations", [])
    resources_to_analyze: List[str] = state.get("resources", [])
    new_recommendations = []

    for resource_id in resources_to_analyze:
        print(f"Analyzing security for resource: {resource_id}")
        properties = azure.get_apim_properties(resource_id)
        instance_name = properties.get("name", "unknown")

        # 1. Check for public management endpoint
        if properties.get("properties", {}).get("publicIpAddressId"):
            rec = {
                "id": f"REC-SEC-PUB-IP-{instance_name}",
                "type": "SECURITY_HARDEN",
                "resource_id": resource_id,
                "details": "Instance has a public IP address for the management endpoint, increasing exposure. Consider using a private VNet integration.",
                "status": "pending_approval", "source_node": "SecurityHardeningNode",
                "payload": {"finding": "Public Management Endpoint"}
            }
            new_recommendations.append(rec)
            print(f"  - Found public management endpoint for {instance_name}")

        # 2. Check for insecure protocols and ciphers
        custom_properties = properties.get("properties", {}).get("customProperties", {})
        for prop, reason in INSECURE_PROTOCOLS.items():
            if custom_properties.get(prop) == "True":
                rec = {
                    "id": f"REC-SEC-PROTO-{prop.split('.')[-1]}-{instance_name}",
                    "type": "SECURITY_HARDEN", "resource_id": resource_id,
                    "details": f"Insecure protocol enabled: {reason}",
                    "status": "pending_approval", "source_node": "SecurityHardeningNode",
                    "payload": {"finding": "Weak TLS Protocol", "protocol": prop}
                }
                new_recommendations.append(rec)
                print(f"  - Found insecure protocol {prop} for {instance_name}")

        for prop, reason in INSECURE_CIPHERS.items():
            if custom_properties.get(prop) == "True":
                rec = {
                    "id": f"REC-SEC-CIPHER-{prop.split('.')[-1]}-{instance_name}",
                    "type": "SECURITY_HARDEN", "resource_id": resource_id,
                    "details": f"Insecure cipher enabled: {reason}",
                    "status": "pending_approval", "source_node": "SecurityHardeningNode",
                    "payload": {"finding": "Weak Cipher", "cipher": prop}
                }
                new_recommendations.append(rec)
                print(f"  - Found insecure cipher {prop} for {instance_name}")

    print(f"Generated {len(new_recommendations)} security hardening recommendations.")
    return {"recommendations": current_recommendations + new_recommendations}
