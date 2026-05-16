def build_mitigation_prompt(
    scored_threats: list[dict],
    context_chunks: str,
) -> str:
    threats_str = "\n".join(
        f"- [{t['stride_category']}] (Risk: {t.get('risk_level', 'N/A')} / {t.get('risk_score', '?')}) {t['description']}"
        for t in scored_threats
    )

    return f"""You are a security controls expert. For each identified threat, recommend specific mitigation actions based on the organization's security standards.

Relevant organizational standards:
{context_chunks}

Threats requiring mitigations:
{threats_str}

For each threat, provide:
1. Recommended mitigation actions (concrete steps)
2. Reference to the specific organizational standard that supports this mitigation
3. Priority level (P0=immediate, P1=short-term, P2=long-term)

Respond in this exact JSON format (no markdown, no code fences):
{{
  "mitigations": [
    {{
      "stride_category": "...",
      "description": "<brief threat description>",
      "actions": ["action 1", "action 2", ...],
      "source_standard": "<standard name or null>",
      "priority": "P0|P1|P2"
    }}
  ]
}}"""
