"""
Graph Engine
------------
Loads network topology and performs:
- Impact analysis (which sites/apps are affected)
- Rerouting (which alternate path to use)

Uses NetworkX. All decisions are deterministic.
The LLM never makes routing decisions.
"""

import json
import os
import networkx as nx


TOPOLOGY_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "topology", "topology.json"
)


class GraphEngine:

    def __init__(self):
        self.graph = nx.DiGraph()
        self.topology = {}
        self.load_topology()

    def load_topology(self):
        with open(TOPOLOGY_PATH, "r") as f:
            self.topology = json.load(f)

        for node in self.topology["nodes"]:
            self.graph.add_node(node["id"], **node)

        for edge in self.topology["edges"]:
            self.graph.add_edge(
                edge["source"], edge["target"],
                tunnel=edge["tunnel"],
                type=edge["type"],
                bandwidth=edge["bandwidth_mbps"],
                primary=edge.get("primary", True),
                backup=edge.get("backup", False),
            )

    def get_affected_sites(self, failed_location: str) -> list:
        """
        Find all sites that depend on the failed location.
        If Hub fails → all branches are affected.
        If Branch fails → only that branch.
        """
        affected = []

        node_data = self.topology["nodes"]
        node_map = {n["id"]: n for n in node_data}

        if node_map.get(failed_location, {}).get("type") in ("hub", "datacenter"):
            # All downstream branches are affected
            for node in node_data:
                if node["type"] == "branch":
                    affected.append(node["id"])
        else:
            affected.append(failed_location)

        return affected

    def get_affected_apps(self, affected_sites: list) -> list:
        """Return all unique apps running on affected sites."""
        apps = set()
        node_map = {n["id"]: n for n in self.topology["nodes"]}
        for site in affected_sites:
            site_apps = node_map.get(site, {}).get("apps", [])
            apps.update(site_apps)
        return sorted(list(apps))

    def find_reroute(self, failed_location: str) -> str:
        """
        Find a backup tunnel/path that bypasses the failed location.
        Returns tunnel name or 'No alternate path found'.
        """
        for edge in self.topology["edges"]:
            if edge.get("backup") and edge["source"] != failed_location and edge["target"] != failed_location:
                return edge["tunnel"]

        return "No alternate path found"

    def analyze(self, gated_failure: dict) -> dict:
        """
        Full impact analysis given a gated failure prediction.
        Input : CONFIDENCE_GATE_OUTPUT
        Output: GRAPH_OUTPUT
        """
        if not gated_failure.get("passed"):
            return {
                "affected_sites": [],
                "affected_apps": [],
                "reroute": "N/A",
                "impact_score": 0.0,
            }

        location = gated_failure["location"]
        affected_sites = self.get_affected_sites(location)
        affected_apps = self.get_affected_apps(affected_sites)
        reroute = self.find_reroute(location)

        # Simple impact score: sites * 20 + critical apps * 10
        app_priorities = self.topology.get("applications", {})
        impact_score = len(affected_sites) * 20
        for app in affected_apps:
            if app_priorities.get(app, {}).get("priority") == "critical":
                impact_score += 15
            elif app_priorities.get(app, {}).get("priority") == "high":
                impact_score += 10

        return {
            "affected_sites": affected_sites,
            "affected_apps": affected_apps,
            "reroute": reroute,
            "impact_score": min(impact_score, 100),
        }


if __name__ == "__main__":
    engine = GraphEngine()
    gated = {
        "passed": True,
        "failure": "MPLS Congestion",
        "confidence": 94.0,
        "time_to_impact": "5 min",
        "location": "Hub",
    }
    result = engine.analyze(gated)
    print(result)