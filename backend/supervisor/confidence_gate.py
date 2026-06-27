"""
Confidence Gate
---------------
Filters out low-confidence failure predictions to reduce alert fatigue.
Threshold: 70% (configurable)
"""

CONFIDENCE_THRESHOLD = 70.0


def confidence_gate(failure_output: dict) -> dict:
    """
    Input  : FAILURE_WORKER_OUTPUT
    Output : CONFIDENCE_GATE_OUTPUT
    """
    if failure_output["failure"] == "None":
        return {
            "passed": False,
            "failure": "None",
            "confidence": 0.0,
            "time_to_impact": "N/A",
            "location": "N/A",
        }

    passed = failure_output["confidence"] >= CONFIDENCE_THRESHOLD

    return {
        "passed": passed,
        "failure": failure_output["failure"],
        "confidence": failure_output["confidence"],
        "time_to_impact": failure_output["time_to_impact"],
        "location": failure_output["location"],
    }


def pick_highest(failure_outputs: list) -> dict:
    """
    When multiple failure workers fire, pick the one with highest confidence.
    Then run it through the gate.
    """
    real_failures = [f for f in failure_outputs if f["failure"] != "None"]

    if not real_failures:
        return confidence_gate({"failure": "None", "confidence": 0.0,
                                 "time_to_impact": "N/A", "location": "N/A"})

    best = max(real_failures, key=lambda f: f["confidence"])
    return confidence_gate(best)