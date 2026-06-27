"""
Bandwidth Signal Worker
-----------------------
Input  : telemetry snapshot (dict)
Output : SIGNAL_WORKER_OUTPUT (dict)
"""


class BandwidthWorker:

    THRESHOLDS = {
        "saturated":  10,
        "high":       25,
        "medium":     50,
        "low":        70,
    }

    def preprocess(self, telemetry: dict) -> dict:
        return {
            "bandwidth_mbps": telemetry.get("bandwidth_mbps", 100),
            "location": telemetry.get("location", "Unknown"),
        }

    def predict(self, data: dict) -> dict:
        bw = data["bandwidth_mbps"]

        if bw <= self.THRESHOLDS["saturated"]:
            prediction = "Bandwidth Saturation — Critical"
            confidence = 96.0
            severity = "Critical"
            time_to_impact = "Now"
        elif bw <= self.THRESHOLDS["high"]:
            prediction = "Bandwidth Saturation — High"
            confidence = 87.0
            severity = "High"
            time_to_impact = "8 min"
        elif bw <= self.THRESHOLDS["medium"]:
            prediction = "Bandwidth Utilization High"
            confidence = 72.0
            severity = "Medium"
            time_to_impact = "20 min"
        elif bw <= self.THRESHOLDS["low"]:
            prediction = "Bandwidth Utilization Elevated"
            confidence = 55.0
            severity = "Low"
            time_to_impact = "40 min"
        else:
            prediction = "Normal"
            confidence = 99.0
            severity = "None"
            time_to_impact = "N/A"

        return {
            "worker": "Bandwidth",
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
    sample = {"bandwidth_mbps": 8, "location": "Branch1"}
    worker = BandwidthWorker()
    print(worker.run(sample))