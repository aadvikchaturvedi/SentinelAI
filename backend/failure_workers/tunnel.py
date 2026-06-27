"""
Tunnel Failure Worker
----------------------
Consumes outputs from: Tunnel worker.
Detects: IPSec Tunnel Failure
Output : FAILURE_WORKER_OUTPUT (dict)
"""


class TunnelFailureWorker:

    def run(self, signal_outputs: list) -> dict:
        tunnel = next((s for s in signal_outputs if s["worker"] == "Tunnel"), None)

        if not tunnel or tunnel["severity"] == "None":
            return {
                "failure": "None",
                "confidence": 0.0,
                "time_to_impact": "N/A",
                "location": "N/A",
            }

        return {
            "failure": "Tunnel Failure",
            "confidence": round(tunnel["confidence"], 1),
            "time_to_impact": tunnel["time_to_impact"],
            "location": tunnel["location"],
        }