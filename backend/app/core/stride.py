STRIDE_CATEGORIES = [
    "Spoofing",
    "Tampering",
    "Repudiation",
    "InformationDisclosure",
    "DenialOfService",
    "ElevationOfPrivilege",
]

STRIDE_DESCRIPTIONS = {
    "Spoofing": "Impersonating a user, process, or external entity to bypass authentication",
    "Tampering": "Maliciously modifying data or code in transit or at rest",
    "Repudiation": "Performing an action without the ability to prove it occurred",
    "InformationDisclosure": "Exposing protected data to unauthorized parties",
    "DenialOfService": "Degrading or denying legitimate access to services or data",
    "ElevationOfPrivilege": "Gaining capabilities or permissions beyond what was authorized",
}


def build_stride_prompt(
    component: str,
    component_type: str,
    data_flows: list[dict],
    trust_boundaries: list[str],
    context_chunks: str,
) -> str:
    flows_str = "\n".join(
        f"  - {f.get('source', '?')} → {f.get('target', '?')}: {f.get('protocol', '?')} / {f.get('data', '?')}"
        for f in data_flows
    ) or "  (none specified)"

    boundaries_str = "\n".join(f"  - {b}" for b in trust_boundaries) or "  (none specified)"

    return f"""You are a threat modeling expert using the STRIDE framework. Analyze the following system component for potential threats.

System Component:
- Name: {component}
- Type: {component_type}

Data flows involving this component:
{flows_str}

Trust boundaries:
{boundaries_str}

Relevant organizational standards:
{context_chunks}

For each STRIDE category below, determine if this component is vulnerable. For each identified threat:
1. Provide a concise description of the threat scenario
2. Rate confidence (High/Medium/Low)
3. Reference the relevant standard if applicable

STRIDE Categories:
{chr(10).join(f'- {k}: {v}' for k, v in STRIDE_DESCRIPTIONS.items())}

Respond in this exact JSON format (no markdown, no code fences):
{{
  "threats": [
    {{
      "stride_category": "Spoofing",
      "threat_present": true/false,
      "description": "...",
      "confidence": "High/Medium/Low",
      "relevant_standard": "..." or null
    }}
  ]
}}

Only include categories where threat_present is true."""
