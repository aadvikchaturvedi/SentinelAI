"""
Routing Instability Failure Worker
------------------------------------
Consumes outputs from: Routing worker.
Detects: BGP/OSPF Route Instability
Output : FAILURE_WORKER_OUTPUT (dict)
"""


class RoutingFailureWorker:

    def run(self, signal_outputs: list) -> dict:
        routing = next((s for s in signal_outputs if s["worker"] == "Routing"), None)

        if not routing or routing["severity"] == "None":
            return {
                "failure": "None",
                "confidence": 0.0,
                "time_to_impact": "N/A",
                "location": "N/A",
            }

        return {
            "failure": "Routing Instability",
            "confidence": round(routing["confidence"], 1),
            "time_to_impact": routing["time_to_impact"],
            "location": routing["location"],
        }