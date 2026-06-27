"""
Jitter Signal Worker
--------------------
Input  : telemetry snapshot (dict)
Output : SIGNAL_WORKER_OUTPUT (dict)
"""


class JitterWorker:

    def preprocess(self, telemetry: dict) -> dict:
        return {
            "jitter_ms": telemetry.get("jitter_ms", 0),
            "location": telemetry.get("location", "Unknown"),
        }

    def predict(self, data: dict) -> dict:
        jitter = data["jitter_ms"]

        if jitter >= 50:
            prediction = "Severe Jitter — Voice/Video Unusable"
            confidence = 95.0
            severity = "Critical"
            time_to_impact = "Now"
        elif jitter >= 25:
            prediction = "High Jitter Growth"
            confidence = 85.0
            severity = "High"
            time_to_impact = "7 min"
        elif jitter >= 12:
            prediction = "Jitter Elevated"
            confidence = 70.0
            severity = "Medium"
            time_to_impact = "20 min"
        elif jitter >= 6:
            prediction = "Jitter Trending Up"
            confidence = 55.0
            severity = "Low"
            time_to_impact = "40 min"
        else:
            prediction = "Normal"
            confidence = 99.0
            severity = "None"
            time_to_impact = "N/A"

        return {
            "worker": "Jitter",
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
    sample = {"jitter_ms": 35, "location": "Hub"}
    worker = JitterWorker()
    print(worker.run(sample))