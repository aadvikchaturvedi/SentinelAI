"""
Congestion Failure Worker
--------------------------
Consumes outputs from: Latency, Bandwidth, PacketLoss, Jitter workers.
Detects: MPLS Congestion
Output : FAILURE_WORKER_OUTPUT (dict)
"""


class CongestionWorker:

    CONFIDENCE_THRESHOLD = 70.0

    def run(self, signal_outputs: list) -> dict:
        """
        signal_outputs: list of SIGNAL_WORKER_OUTPUT dicts
        """
        relevant = {s["worker"]: s for s in signal_outputs
                    if s["worker"] in ("Latency", "Bandwidth", "PacketLoss", "Jitter")}

        triggered = [s for s in relevant.values()
                     if s["severity"] in ("High", "Critical")
                     and s["confidence"] >= self.CONFIDENCE_THRESHOLD]

        if not triggered:
            return {
                "failure": "None",
                "confidence": 0.0,
                "time_to_impact": "N/A",
                "location": "N/A",
            }

        # Confidence is average of triggered workers, boosted by count
        avg_confidence = sum(s["confidence"] for s in triggered) / len(triggered)
        boost = min(len(triggered) * 3, 10)
        final_confidence = min(avg_confidence + boost, 99.0)

        # Take the earliest time_to_impact
        times = [s["time_to_impact"] for s in triggered if s["time_to_impact"] != "N/A"]
        time_to_impact = times[0] if times else "Unknown"

        # Location from highest confidence worker
        location = max(triggered, key=lambda s: s["confidence"])["location"]

        return {
            "failure": "MPLS Congestion",
            "confidence": round(final_confidence, 1),
            "time_to_impact": time_to_impact,
            "location": location,
        }


if __name__ == "__main__":
    sample_signals = [
        {"worker": "Latency", "prediction": "Latency Drift — High", "confidence": 88, "severity": "High", "time_to_impact": "5 min", "location": "Hub"},
        {"worker": "Bandwidth", "prediction": "Bandwidth Saturation", "confidence": 87, "severity": "High", "time_to_impact": "8 min", "location": "Hub"},
        {"worker": "PacketLoss", "prediction": "High Packet Loss", "confidence": 90, "severity": "High", "time_to_impact": "5 min", "location": "Hub"},
        {"worker": "Jitter", "prediction": "Normal", "confidence": 99, "severity": "None", "time_to_impact": "N/A", "location": "Hub"},
    ]
    worker = CongestionWorker()
    print(worker.run(sample_signals))