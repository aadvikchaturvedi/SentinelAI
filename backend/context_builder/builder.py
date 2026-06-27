"""
Context Builder
---------------
Assembles outputs from Failure Workers, Graph Engine, and RAG
into a single structured JSON that becomes the ONLY input to the LLM.

This prevents prompt chaos and keeps the LLM focused on explaining,
not on parsing raw telemetry.
"""


def build_context(gated_failure: dict, graph_output: dict, rag_output: dict) -> dict:
    """
    Input:
        gated_failure : CONFIDENCE_GATE_OUTPUT
        graph_output  : GRAPH_OUTPUT
        rag_output    : RAG_OUTPUT
    Output:
        CONTEXT_OUTPUT (passed directly to LLM)
    """
    return {
        "failure":        gated_failure.get("failure", "None"),
        "confidence":     gated_failure.get("confidence", 0.0),
        "time_to_impact": gated_failure.get("time_to_impact", "N/A"),
        "location":       gated_failure.get("location", "Unknown"),
        "graph": {
            "affected_sites": graph_output.get("affected_sites", []),
            "affected_apps":  graph_output.get("affected_apps", []),
            "reroute":        graph_output.get("reroute", "N/A"),
            "impact_score":   graph_output.get("impact_score", 0),
        },
        "rag": {
            "runbook":  rag_output.get("runbook", ""),
            "sop":      rag_output.get("sop", ""),
            "incident": rag_output.get("incident", ""),
        },
    }


if __name__ == "__main__":
    import json

    gated = {
        "passed": True,
        "failure": "MPLS Congestion",
        "confidence": 94.0,
        "time_to_impact": "5 min",
        "location": "Hub",
    }
    graph = {
        "affected_sites": ["Branch1", "Branch2"],
        "affected_apps": ["ERP", "Video"],
        "reroute": "Tunnel-B",
        "impact_score": 75,
    }
    rag = {
        "runbook": "RUNBOOK: MPLS Congestion...",
        "sop": "SOP: Packet Loss Response...",
        "incident": "INCIDENT: #42...",
    }

    context = build_context(gated, graph, rag)
    print(json.dumps(context, indent=2))