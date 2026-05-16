DREAD_CATEGORIES = [
    "Damage",
    "Reproducibility",
    "Exploitability",
    "AffectedUsers",
    "Discoverability",
]

DREAD_DESCRIPTIONS = {
    "Damage": "How severe is the impact? (1=minor info leak, 10=complete system compromise)",
    "Reproducibility": "How easily can the attack be reproduced? (1=extremely hard, 10=trivially)",
    "Exploitability": "How easy is it to launch the attack? (1=requires insider+physical access, 10=unauthenticated remote)",
    "AffectedUsers": "How many users are impacted? (1=single user, 10=all users)",
    "Discoverability": "How easy is the vulnerability to find? (1=extremely obscure, 10=publicly known)",
}


def build_dread_prompt(threats: list[dict], context_chunks: str) -> str:
    threats_str = "\n".join(
        f"- [{t['stride_category']}] {t['description']} (confidence: {t.get('confidence', 'Medium')})"
        for t in threats
    )

    return f"""You are a risk assessment expert using the DREAD framework. Score each threat below.

Relevant organizational standards:
{context_chunks}

Threats to score:
{threats_str}

Score each threat on a scale of 1-10 for each DREAD dimension:
{chr(10).join(f'- {k}: {v}' for k, v in DREAD_DESCRIPTIONS.items())}

The overall risk score = (Damage + Reproducibility + Exploitability + AffectedUsers + Discoverability) / 5

Risk levels: 0-3 Low, 3-6 Medium, 6-8 High, 8-10 Critical

Respond in this exact JSON format (no markdown, no code fences):
{{
  "scored_threats": [
    {{
      "stride_category": "...",
      "description": "...",
      "dread_scores": {{
        "Damage": <int 1-10>,
        "Reproducibility": <int 1-10>,
        "Exploitability": <int 1-10>,
        "AffectedUsers": <int 1-10>,
        "Discoverability": <int 1-10>
      }},
      "risk_score": <float>,
      "risk_level": "Low|Medium|High|Critical"
    }}
  ]
}}"""
