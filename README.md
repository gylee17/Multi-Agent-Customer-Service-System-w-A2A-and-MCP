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

Multi-Agent-Customer-Service-System-w-A2A-and-MCP/
├── mcp_server/
│   ├── database_setup.py      # already there
│   ├── db.py                  # DB connection helper (you already have)
│   ├── tools.py               # DB queries (you already have)
│   └── mcp_server.py          # real MCP server exposing tools
│
├── agents/
│   ├── router_agent_llm.py    # LLM-backed Router Agent
│   ├── data_agent_llm.py      # LLM-backed Customer Data Agent
│   └── support_agent_llm.py   # LLM-backed Support Agent
│
├── demo/
│   ├── run_scenarios_llm.py   # A2A flows using lab-style pattern
│   └── A2A_demo_notebook.ipynb  # Colab-based demo
│
├── requirements.txt
└── README.md

```


## 2. Requirements

This project uses Python standard library only.

requirements.txt includes:

```text
# No external dependencies required — all functionality uses Python standard library only.
```

## 3. Setup Instructions

Follow these steps to set up and run the system.

  ## 3.1 Clone the Repository
  
  ```text
  git clone https://github.com/<your-username>/Multi-Agent-Customer-Service-System-w-A2A-and-MCP.git
  cd Multi-Agent-Customer-Service-System-w-A2A-and-MCP
  ```

  ## 3.2 Create and Activate Virtual Environment

  ```text
  python3 -m venv .venv
  source .venv/bin/activate
  ```

You should now see (.venv) in your terminal prompt.

  ## 3.3 Install Requirements
  ```text
  pip install -r requirements.txt
  ```

  ## 3.4 Initialize the Database
  
  ```text
  cd mcp_server
  python database_setup.py
  ```

When prompted:
  ```text
  Would you like to insert sample data? (y/n): y
  ```

Verify the database:
  ```text
  ls
  # support.db should now be visible
  ```

Return to project root:

  ```text
  cd ..
  ```

## 4. Running the System

Run the full multi-agent demonstration:

```text
python -m demo.run_scenarios
```

This outputs:

- Full A2A communication logs
- Router ↔ Data Agent ↔ Support Agent interactions
- Final composed responses

## 5. Test Scenarios Implemented

The system handles all required assignment scenarios:

  - 1. Simple Query: "Get customer information for ID 5"
  - 2. Coordinated Query: "I'm customer 12345 and need help upgrading my account"
  - 3. Complex Query: "Show me all active customers who have open tickets"
  - 4. Escalation: "I've been charged twice, please refund immediately!"
  - 5. Multi-Intent: "Update my email to new@email.com and show my ticket history"


Each scenario prints detailed step-by-step A2A logs.

## 6. Notebook Demo

A Jupyter Notebook version is available at:

```text
demo/A2A_demo_notebook.ipynb
```

It includes:

  - Initialization steps
  - Agent imports
  - Scenario walkthroughs
  - Consolidated results
