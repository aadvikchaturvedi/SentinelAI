# contracts.py
# Every module in the pipeline communicates using these schemas.
# Never pass raw data between modules — always use these contracts.

# ----------------------------
# TELEMETRY INPUT
# ----------------------------
TELEMETRY_SCHEMA = {
    "timestamp": "str",
    "location": "str",         # e.g. "Hub", "Branch1"
    "latency_ms": "float",
    "bandwidth_mbps": "float",
    "packet_loss_pct": "float",
    "cpu_pct": "float",
    "jitter_ms": "float",
    "bgp_events": "int",
    "ospf_events": "int",
    "tunnel_latency_ms": "float",
    "tunnel_packet_loss_pct": "float"
}

# ----------------------------
# SIGNAL WORKER OUTPUT
# ----------------------------
SIGNAL_WORKER_OUTPUT = {
    "worker": "str",           # e.g. "Latency"
    "prediction": "str",       # e.g. "Latency Drift"
    "confidence": "float",     # 0-100
    "severity": "str",         # "Low" | "Medium" | "High" | "Critical"
    "time_to_impact": "str",   # e.g. "20 min"
    "location": "str"          # e.g. "Hub"
}

# ----------------------------
# FAILURE WORKER OUTPUT
# ----------------------------
FAILURE_WORKER_OUTPUT = {
    "failure": "str",          # e.g. "MPLS Congestion"
    "confidence": "float",     # 0-100
    "time_to_impact": "str",
    "location": "str"
}

# ----------------------------
# CONFIDENCE GATE OUTPUT
# ----------------------------
CONFIDENCE_GATE_OUTPUT = {
    "passed": "bool",
    "failure": "str",
    "confidence": "float",
    "time_to_impact": "str",
    "location": "str"
}

# ----------------------------
# GRAPH ENGINE OUTPUT
# ----------------------------
GRAPH_OUTPUT = {
    "affected_sites": ["str"],
    "affected_apps": ["str"],
    "reroute": "str",          # e.g. "Tunnel-B"
    "impact_score": "float"
}

# ----------------------------
# RAG OUTPUT
# ----------------------------
RAG_OUTPUT = {
    "runbook": "str",
    "sop": "str",
    "incident": "str"
}

# ----------------------------
# CONTEXT BUILDER OUTPUT (input to LLM)
# ----------------------------
CONTEXT_OUTPUT = {
    "failure": "str",
    "confidence": "float",
    "time_to_impact": "str",
    "location": "str",
    "graph": GRAPH_OUTPUT,
    "rag": RAG_OUTPUT
}

# ----------------------------
# LLM OUTPUT
# ----------------------------
LLM_OUTPUT = {
    "explanation": "str",
    "recommended_actions": ["str"],
    "severity": "str"
}

# ----------------------------
# FINAL API RESPONSE
# ----------------------------
API_RESPONSE = {
    "status": "str",
    "prediction": FAILURE_WORKER_OUTPUT,
    "graph": GRAPH_OUTPUT,
    "rag": RAG_OUTPUT,
    "llm": LLM_OUTPUT,
    "timestamp": "str"
}