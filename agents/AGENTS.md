# Lyzr Agents & Orchestration

This folder contains the core persona instructions and configurations used to generate the autonomous Buyer and Vendor agents on the **Lyzr Agent Studio** platform.

## 🧠 Lyzr Studio Configurations
Because our architecture uses the Lyzr Inference API (`v3/inference/chat/`), the raw LLM personas are configured directly in the Lyzr Studio. We have exported their system prompts here for the judges' reference:
* `buyer_agent_prompt.txt` - The aggressive procurement persona.
* `vendor_agent_prompt.txt` - The defensive sales persona.

## ⚙️ Orchestration & Safe AI Arbiter (Execution Logic)
While the AI personas are defined above, the actual **game-theoretic orchestration** and **Safe AI guardrails** are deeply integrated into our FastAPI backend to ensure production-grade security and zero hallucinations.

If you are evaluating our orchestration logic, please navigate to the following directories in our repository:

1. **The Safe AI Arbiter:** [`../backend/app/agents/arbiter.py`](../backend/app/agents/arbiter.py)
   * Deterministically intercepts and validates every single Lyzr LLM output against the user's hard limits (Max Budget, Min SLA).
2. **The Turn-Based Orchestrator:** [`../backend/app/engine/orchestrator.py`](../backend/app/engine/orchestrator.py)
   * Manages the state machine, calculates dynamic concessions, injects context into the Lyzr API, and forces LLM retries if the Arbiter detects a hallucination.
3. **Agent Integration Classes:** [`../backend/app/agents/`](../backend/app/agents/)
   * The Python wrapper classes (`buyer.py`, `vendor.py`) that interface with the Lyzr API.
