import json
import re

from app.core.dread import build_dread_prompt
from app.core.llm_provider import get_llm as _get_llm
from app.core.mitigations import build_mitigation_prompt
from app.core.stride import build_stride_prompt
from app.ingestion.vectorstore import similarity_search


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        text = text[start : end + 1]
    return json.loads(text)


def _retrieve_context(query: str, k: int = 5) -> str:
    docs = similarity_search(query, k=k)
    if not docs:
        return "No specific organizational standards found. Use general best practices."
    parts = []
    for doc in docs:
        source = doc.metadata.get("source", "unknown")
        parts.append(f"[Source: {source}]\n{doc.page_content}")
    return "\n\n".join(parts)


def _llm_json(prompt: str) -> dict:
    llm = _get_llm()
    raw = llm.invoke(prompt)
    content = raw if isinstance(raw, str) else raw.content
    return _extract_json(content)


def analyze_component(
    component: str,
    component_type: str,
    data_flows: list[dict],
    trust_boundaries: list[str],
    session_context: str = "",
) -> dict:
    context = _retrieve_context(f"threat modeling {component} {component_type} security standards")
    if session_context:
        context = f"Session context:\n{session_context}\n\n{context}"

    stride_prompt = build_stride_prompt(component, component_type, data_flows, trust_boundaries, context)
    stride_result = _llm_json(stride_prompt)
    threats = stride_result.get("threats", [])

    if not threats:
        return {
            "component": component,
            "threats": [],
            "scored_threats": [],
            "mitigations": [],
        }

    dread_prompt = build_dread_prompt(threats, context)
    dread_result = _llm_json(dread_prompt)
    scored_threats = dread_result.get("scored_threats", [])

    mitigation_prompt = build_mitigation_prompt(scored_threats, context)
    mitigation_result = _llm_json(mitigation_prompt)
    mitigations = mitigation_result.get("mitigations", [])

    return {
        "component": component,
        "threats": threats,
        "scored_threats": scored_threats,
        "mitigations": mitigations,
    }


def analyze_full_model(
    components: list[dict],
    data_flows: list[dict],
    trust_boundaries: list[str],
    session_context: str = "",
) -> list[dict]:
    results = []
    for comp in components:
        name = comp.get("name", "unknown")
        comp_type = comp.get("type", "component")
        comp_flows = [
            f for f in data_flows
            if f.get("source") == name or f.get("target") == name
        ]
        result = analyze_component(name, comp_type, comp_flows, trust_boundaries, session_context)
        results.append(result)
    return results
