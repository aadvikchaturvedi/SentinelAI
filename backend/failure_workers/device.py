"""
Device Failure Worker
----------------------
Consumes outputs from: CPU worker.
Detects: Device/Router Overload
Output : FAILURE_WORKER_OUTPUT (dict)
"""


class DeviceFailureWorker:

    def run(self, signal_outputs: list) -> dict:
        cpu = next((s for s in signal_outputs if s["worker"] == "CPU"), None)

        if not cpu or cpu["severity"] == "None":
            return {
                "failure": "None",
                "confidence": 0.0,
                "time_to_impact": "N/A",
                "location": "N/A",
            }

        return {
            "failure": "Device Overload",
            "confidence": round(cpu["confidence"], 1),
            "time_to_impact": cpu["time_to_impact"],
            "location": cpu["location"],
        }