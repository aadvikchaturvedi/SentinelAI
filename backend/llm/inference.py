"""
LLM Inference
-------------
Sends structured context to Ollama (local, offline).
The LLM ONLY explains. It never predicts, reroutes, or calculates impact.
All decisions are made upstream by rule-based workers and the graph engine.
"""

import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5"


SYSTEM_PROMPT = """You are an AI Copilot for a Network Operations Center (NOC).
You are monitoring an air-gapped MPLS/SD-WAN network.

Your ONLY job is to explain predictions that were already made by the system.
You do NOT make predictions yourself.
You do NOT calculate impact yourself.
You do NOT decide routing yourself.

All predictions, affected sites, affected applications, and rerouting paths
are provided to you as structured data. You ONLY explain them clearly.

Always respond in JSON with this exact structure:
{
  "explanation": "Clear explanation of what is happening and why",
  "recommended_actions": ["Action 1", "Action 2", "Action 3"],
  "severity": "Low | Medium | High | Critical"
}

Be concise, professional, and actionable. Maximum 3 sentences for explanation.
Maximum 4 recommended actions."""


def build_prompt(context: dict) -> str:
    """Convert context JSON into a clear user prompt for the LLM."""
    failure       = context.get("failure", "None")
    confidence    = context.get("confidence", 0)
    time_to_impact= context.get("time_to_impact", "N/A")
    location      = context.get("location", "Unknown")
    graph         = context.get("graph", {})
    rag           = context.get("rag", {})

    affected_sites = ", ".join(graph.get("affected_sites", [])) or "None"
    affected_apps  = ", ".join(graph.get("affected_apps",  [])) or "None"
    reroute        = graph.get("reroute", "N/A")

    runbook  = rag.get("runbook",  "")[:500]  # Truncate to keep prompt manageable
    sop      = rag.get("sop",      "")[:300]
    incident = rag.get("incident", "")[:300]

    return f"""NETWORK ALERT - Explain this to the NOC operator:

FAILURE DETECTED: {failure}
CONFIDENCE: {confidence}%
TIME TO IMPACT: {time_to_impact}
LOCATION: {location}
AFFECTED SITES: {affected_sites}
AFFECTED APPLICATIONS: {affected_apps}
RECOMMENDED REROUTE: {reroute}

RELEVANT RUNBOOK:
{runbook}

RELEVANT SOP:
{sop}

SIMILAR PAST INCIDENT:
{incident}

Respond ONLY with the JSON structure specified. No additional text."""


def query_llm(context: dict) -> dict:
    """
    Send context to Ollama and get structured explanation.
    Returns LLM_OUTPUT dict.
    """
    prompt = build_prompt(context)

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "system": SYSTEM_PROMPT,
                "stream": False,
                "format": "json",
            },
            timeout=60,
        )
        response.raise_for_status()
        raw = response.json().get("response", "{}")
        parsed = json.loads(raw)
        return {
            "explanation": parsed.get("explanation", "No explanation generated."),
            "recommended_actions": parsed.get("recommended_actions", []),
            "severity": parsed.get("severity", "Unknown"),
        }

    except requests.exceptions.ConnectionError:
        return {
            "explanation": "LLM offline. Prediction system is still fully operational. Please start Ollama.",
            "recommended_actions": ["Run: ollama serve", "Run: ollama pull qwen2.5"],
            "severity": context.get("gated", {}).get("failure", "Unknown"),
        }
    except Exception as e:
        return {
            "explanation": f"LLM error: {str(e)}",
            "recommended_actions": [],
            "severity": "Unknown",
        }


def query_chat(question: str, context: dict) -> str:
    """
    For the copilot chat interface — answer an operator's freeform question.
    """
    failure    = context.get("failure", "None")
    location   = context.get("location", "Unknown")
    reroute    = context.get("graph", {}).get("reroute", "N/A")

    prompt = f"""Current network status:
- Active Failure: {failure}
- Location: {location}
- Recommended Reroute: {reroute}

Operator question: {question}

Answer concisely and professionally. Maximum 3 sentences."""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "system": SYSTEM_PROMPT,
                "stream": False,
            },
            timeout=60,
        )
        response.raise_for_status()
        return response.json().get("response", "No response from LLM.")
    except Exception as e:
        return f"LLM unavailable: {str(e)}"


if __name__ == "__main__":
    sample_context = {
        "failure": "MPLS Congestion",
        "confidence": 94.0,
        "time_to_impact": "5 min",
        "location": "Hub",
        "graph": {
            "affected_sites": ["Branch1", "Branch2"],
            "affected_apps": ["ERP", "Video"],
            "reroute": "Tunnel-B",
            "impact_score": 75,
        },
        "rag": {
            "runbook": "RUNBOOK: MPLS Congestion — shift traffic to Tunnel-B, prioritize ERP.",
            "sop": "SOP: Packet loss above 3% — escalate to Network Lead.",
            "incident": "Incident #42: Hub congestion resolved in 12 min by rerouting to Tunnel-B.",
        },
    }
    result = query_llm(sample_context)
    print(result)