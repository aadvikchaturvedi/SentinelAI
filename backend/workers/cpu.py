"""
CPU Signal Worker
-----------------
Input  : telemetry snapshot (dict)
Output : SIGNAL_WORKER_OUTPUT (dict)
"""


class CPUWorker:

    def preprocess(self, telemetry: dict) -> dict:
        return {
            "cpu_pct": telemetry.get("cpu_pct", 0),
            "location": telemetry.get("location", "Unknown"),
        }

    def predict(self, data: dict) -> dict:
        cpu = data["cpu_pct"]

        if cpu >= 95:
            prediction = "CPU Saturation — Critical"
            confidence = 97.0
            severity = "Critical"
            time_to_impact = "Now"
        elif cpu >= 85:
            prediction = "CPU Saturation — High"
            confidence = 89.0
            severity = "High"
            time_to_impact = "5 min"
        elif cpu >= 70:
            prediction = "CPU Utilization Elevated"
            confidence = 74.0
            severity = "Medium"
            time_to_impact = "15 min"
        elif cpu >= 55:
            prediction = "CPU Trending Up"
            confidence = 58.0
            severity = "Low"
            time_to_impact = "35 min"
        else:
            prediction = "Normal"
            confidence = 99.0
            severity = "None"
            time_to_impact = "N/A"

        return {
            "worker": "CPU",
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
    sample = {"cpu_pct": 92, "location": "Datacenter"}
    worker = CPUWorker()
    print(worker.run(sample))