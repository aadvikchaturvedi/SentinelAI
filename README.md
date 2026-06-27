# Air-Gapped Predictive Copilot for Secure MPLS Operations

An offline AI-powered NOC Copilot that predicts network failures before they happen.

## Setup

### 1. Install Ollama
```bash
brew install ollama
ollama pull qwen2.5
ollama serve
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the backend
```bash
cd backend
python main.py
```

### 4. Open the dashboard
```
http://localhost:8000
```

---

## Demo Flow

1. Open `http://localhost:8000`
2. Click **Run Prediction** — see healthy network
3. Click **Inject Congestion (Hub)**
4. Click **Run Prediction** again — see failure predicted with explanation
5. Ask Copilot: *"What should I do right now?"*
6. Click **Clear All Faults** — network returns to healthy

---

## Architecture

```
Synthetic Telemetry
  → Signal Workers (Latency, Bandwidth, CPU, PacketLoss, Jitter, Routing, Tunnel)
  → Failure Workers (Congestion, Routing, Tunnel, Device)
  → Confidence Gate (filters < 70% confidence)
  → Graph Engine (affected sites, apps, rerouting)
  → RAG (runbooks, SOPs, historical incidents)
  → Context Builder (assembles one JSON)
  → Ollama LLM (explains in natural language)
  → FastAPI → Frontend Dashboard
```

## Project Structure

```
backend/
  main.py                  — FastAPI app
  supervisor/supervisor.py — Pipeline orchestrator
  workers/                 — Signal workers (one per metric)
  failure_workers/         — Failure detection workers
  graph/graph.py           — Network topology + impact analysis
  rag/rag.py               — RAG knowledge base
  context_builder/         — Context assembly for LLM
  llm/inference.py         — Ollama LLM client
  telemetry/synthetic.py   — Synthetic telemetry generator
  database/db.py           — SQLite logging

frontend/
  templates/index.html     — Dashboard
  static/css/style.css     — Dark theme
  static/js/app.js         — Dashboard logic

data/
  topology/topology.json   — Network topology
  runbooks/                — MPLS, Tunnel, BGP, CPU runbooks
  sops/                    — Escalation matrix, packet loss SOP
  incidents/               — Historical incidents
```
