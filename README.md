# Multi-Agent Customer Service System (A2A + MCP)

This project implements a multi-agent customer service system where specialized agents coordinate using **Agent-to-Agent (A2A)** communication and access customer data via the **Model Context Protocol (MCP)**.

The system demonstrates:

- Router agent that orchestrates other agents
- Customer Data agent that talks to a SQLite database via MCP tools
- Support agent that handles customer queries, escalation, and reporting
- End-to-end flows for task allocation, negotiation/escalation, and multi-step coordination

---

## 1. Project Structure

```text
.
├─ mcp_server/
│  ├─ database_setup.py      # Creates SQLite DB and inserts test data
│  ├─ db.py                  # SQLite connection helpers
│  ├─ tools.py               # MCP tool implementations
│  └─ server.py              # MCP server entrypoint
│
├─ agents/
│  ├─ base.py                # Shared types (Message, Agent, etc.)
│  ├─ router_agent.py        # Router / orchestrator agent
│  ├─ data_agent.py          # Customer Data agent (uses MCP tools)
│  └─ support_agent.py       # Support agent (support logic & escalation)
│
├─ demo/
│  ├─ run_scenarios.py       # End-to-end demo (CLI)
│  └─ multi_agent_demo.ipynb # (Optional) Colab-style notebook demo
│
├─ requirements.txt
└─ README.md
