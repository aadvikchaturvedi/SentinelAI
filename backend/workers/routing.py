"""
Routing Signal Worker
---------------------
Analyzes BGP events, OSPF events, route flapping.
Input  : telemetry snapshot (dict)
Output : SIGNAL_WORKER_OUTPUT (dict)
"""


class RoutingWorker:

    def preprocess(self, telemetry: dict) -> dict:
        return {
            "bgp_events": telemetry.get("bgp_events", 0),
            "ospf_events": telemetry.get("ospf_events", 0),
            "location": telemetry.get("location", "Unknown"),
        }

    def predict(self, data: dict) -> dict:
        bgp = data["bgp_events"]
        ospf = data["ospf_events"]
        total_events = bgp + ospf

        if total_events >= 20:
            prediction = "Severe Route Flapping"
            confidence = 94.0
            severity = "Critical"
            time_to_impact = "Now"
        elif total_events >= 10:
            prediction = "BGP/OSPF Instability — High"
            confidence = 86.0
            severity = "High"
            time_to_impact = "10 min"
        elif total_events >= 5:
            prediction = "Routing Instability Detected"
            confidence = 72.0
            severity = "Medium"
            time_to_impact = "20 min"
        elif total_events >= 2:
            prediction = "Routing Events Elevated"
            confidence = 58.0
            severity = "Low"
            time_to_impact = "40 min"
        else:
            prediction = "Normal"
            confidence = 99.0
            severity = "None"
            time_to_impact = "N/A"

        return {
            "worker": "Routing",
            "prediction": prediction,
            "confidence": confidence,
            "severity": severity,
            "time_to_impact": time_to_impact,
            "location": data["location"],
        }

    def postprocess(self, result: dict) -> dict:
        result["confidence"] = round(result["confidence"], 1)
        return result

    def run(self, telemetry: dict) -> dict:
        data = self.preprocess(telemetry)
        result = self.predict(data)
        return self.postprocess(result)


if __name__ == "__main__":
    sample = {"bgp_events": 15, "ospf_events": 5, "location": "Hub"}
    worker = RoutingWorker()
    print(worker.run(sample))