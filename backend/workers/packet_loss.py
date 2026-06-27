"""
Packet Loss Signal Worker
-------------------------
Input  : telemetry snapshot (dict)
Output : SIGNAL_WORKER_OUTPUT (dict)
"""


class PacketLossWorker:

    def preprocess(self, telemetry: dict) -> dict:
        return {
            "packet_loss_pct": telemetry.get("packet_loss_pct", 0),
            "location": telemetry.get("location", "Unknown"),
        }

    def predict(self, data: dict) -> dict:
        loss = data["packet_loss_pct"]

        if loss >= 20:
            prediction = "Severe Packet Loss"
            confidence = 97.0
            severity = "Critical"
            time_to_impact = "Now"
        elif loss >= 5:
            prediction = "High Packet Loss"
            confidence = 90.0
            severity = "High"
            time_to_impact = "5 min"
        elif loss >= 2:
            prediction = "Packet Loss Escalation"
            confidence = 76.0
            severity = "Medium"
            time_to_impact = "18 min"
        elif loss >= 0.5:
            prediction = "Packet Loss Detected"
            confidence = 60.0
            severity = "Low"
            time_to_impact = "35 min"
        else:
            prediction = "Normal"
            confidence = 99.0
            severity = "None"
            time_to_impact = "N/A"

        return {
            "worker": "PacketLoss",
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
    sample = {"packet_loss_pct": 7.5, "location": "Branch2"}
    worker = PacketLossWorker()
    print(worker.run(sample))