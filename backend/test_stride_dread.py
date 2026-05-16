"""Test the full STRIDE + DREAD analysis pipeline."""
import json
import requests

BASE = "http://backend:8000"

# Login
r = requests.post(f"{BASE}/auth/login", json={"username": "admin", "password": "admin"})
assert r.status_code == 200
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("✓ Logged in as admin")

# First, upload a security standard for context
standard = b"""
# Corporate Security Policy v3.2

## Authentication Requirements
- All services MUST use OAuth 2.0 / OIDC for authentication
- API keys are only permitted for machine-to-machine communication
- Session tokens expire after 15 minutes
- Multi-factor authentication is required for all administrative access

## Data Protection
- All data in transit MUST use TLS 1.3
- Data at rest MUST use AES-256 encryption
- Personally Identifiable Information (PII) must be encrypted
- Database credentials must be rotated every 90 days

## Logging & Monitoring
- All authentication attempts must be logged
- Security events must be sent to SIEM within 5 minutes
- Audit logs must be immutable and retained for 1 year
"""
r = requests.post(f"{BASE}/ingestion/upload", headers=headers, files={"file": ("security_policy.md", standard, "text/markdown")})
assert r.status_code == 200
print(f"✓ Uploaded security policy ({r.json()['chunk_count']} chunks)")

# Create a threat model
r = requests.post(f"{BASE}/threat-models", headers=headers, json={"name": "Payment Gateway", "description": "Payment processing system"})
assert r.status_code == 201
model_id = r.json()["id"]
print(f"✓ Created threat model #{model_id}")

# Run STRIDE + DREAD analysis
analysis_payload = {
    "components": [
        {"name": "Web Frontend", "type": "web-application"},
        {"name": "API Gateway", "type": "api-gateway"},
        {"name": "Payment Database", "type": "database"},
    ],
    "data_flows": [
        {"source": "Web Frontend", "target": "API Gateway", "protocol": "HTTPS", "data": "User credentials + payment info"},
        {"source": "API Gateway", "target": "Payment Database", "protocol": "TLS", "data": "Transaction records"},
    ],
    "trust_boundaries": [
        "Internet → DMZ (Web Frontend)",
        "DMZ → Internal Network (API Gateway)",
        "Internal Network → Restricted (Payment Database)",
    ],
    "session_context": "This is a PCI DSS compliant payment gateway handling cardholder data.",
}

r = requests.post(f"{BASE}/analysis/run", headers=headers, json=analysis_payload)
assert r.status_code == 200, f"Analysis failed: {r.status_code} {r.text}"
result = r.json()

print(f"\n{'='*60}")
print(f"ANALYSIS RESULTS")
print(f"{'='*60}")
print(f"Total threats found: {result['total_threats']}")
print(f"Average risk score: {result['average_risk_score']}/10")
print(f"Components analyzed: {len(result['components'])}")

for comp in result["components"]:
    print(f"\n── Component: {comp['component']} ──")
    for st in comp.get("scored_threats", []):
        dread = st["dread_scores"]
        print(f"  [{st['risk_level']:>8} / {st['risk_score']:.1f}] "
              f"{st['stride_category']}: {st['description'][:80]}...")
        print(f"    DREAD: D={dread['Damage']} R={dread['Reproducibility']} "
              f"E={dread['Exploitability']} A={dread['AffectedUsers']} D={dread['Discoverability']}")

    for m in comp.get("mitigations", []):
        print(f"  🛡️  Mitigation [{m['priority']}]: {', '.join(m['actions'][:2])}...")
        if m.get("source_standard"):
            print(f"     Source: {m['source_standard']}")

print(f"\n{'='*60}")

# Verify we got meaningful results
assert result["total_threats"] > 0, "No threats identified!"
assert len(result["components"]) == 3, "Should have 3 component analyses"
assert result["average_risk_score"] > 0, "Risk score should be > 0"
print("\n✅ Full STRIDE + DREAD analysis pipeline verified!")
