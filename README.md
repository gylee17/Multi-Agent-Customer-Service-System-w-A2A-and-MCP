# Multi-Agent Customer Service System (A2A + MCP)

This project implements a **multi-agent customer service system** using:

- **Agent-to-Agent (A2A) coordination**
- **Model Context Protocol (MCP) tools**
- **SQLite-based customer + ticket database**
- **Three cooperating agents**:
  - **Router Agent** (orchestrator)
  - **Customer Data Agent** (MCP data specialist)
  - **Support Agent** (support logic, escalation, formatting)

The system handles task allocation, negotiation between agents, and multi-step coordination to answer complex user queries.

---

# Project Structure

Multi-Agent-Customer-Service-System-w-A2A-and-MCP/
│
├── mcp_server/
│ ├── database_setup.py # Creates support.db + sample data
│ ├── support.db # SQLite database (auto-generated)
│ ├── db.py # Database connection helpers
│ └── tools.py # MCP tools (get/update/create/list)
│
├── agents/
│ ├── init.py
│ ├── base.py # Message & Agent base classes
│ ├── data_agent.py # Uses MCP tools
│ ├── support_agent.py # Support logic & escalation
│ └── router_agent.py # Orchestrates A2A interactions
│
├── demo/
│ ├── run_scenarios.py # Full end-to-end demonstration
│ └── A2A_demo_notebook.ipynb
│
├── requirements.txt
└── README.md

yaml
Copy code

---

# Requirements

This project uses **Python standard library only**, so the requirements.txt states:

No external dependencies required; project uses Python standard library only.
yaml
Copy code

This satisfies the requirement for a clear dependency list.

---

# Setup Instructions

Follow these steps exactly to run the system.

---

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/<your-username>/Multi-Agent-Customer-Service-System-w-A2A-and-MCP.git
cd Multi-Agent-Customer-Service-System-w-A2A-and-MCP
2️⃣ Create and Activate Virtual Environment
bash
Copy code
python3 -m venv .venv
source .venv/bin/activate      # macOS / Linux
You should now see (.venv) in your terminal prompt.

3️⃣ Install Requirements
bash
Copy code
pip install -r requirements.txt
4️⃣ Initialize the Database
bash
Copy code
cd mcp_server
python database_setup.py
When prompted:

pgsql
Copy code
Would you like to insert sample data? (y/n): y
Check the database exists:

bash
Copy code
ls
# support.db should appear
Then return to project root:

bash
Copy code
cd ..
▶️ Running the System (All Scenarios)
From the project root folder:

bash
Copy code
python -m demo.run_scenarios
This prints:

Full A2A message logs

Router → DataAgent → SupportAgent communication

Final user-facing answers for each query

🧪 Test Scenarios Implemented
The system fully supports all required assignment scenarios:

✔ Simple Query
“Get customer information for ID 5”

✔ Scenario 1: Task Allocation
“I need help with my account, customer ID 12345”

✔ Scenario 2: Negotiation / Escalation
“I want to cancel my subscription but I'm having billing issues”

✔ Scenario 3: Multi-step Coordination
“What's the status of all high-priority tickets for premium customers?”

✔ Complex Query
“Show me all active customers who have open tickets”

✔ Escalation
“I've been charged twice, please refund immediately!”

✔ Multi-Intent
“Update my email to new@email.com and show my ticket history”

Each scenario logs detailed A2A transitions.

📓 Notebook Demo
A Jupyter Notebook version is included:

Copy code
demo/A2A_demo_notebook.ipynb
It contains:

Explanation of setup

Agent imports

Helper functions

Execution of all scenarios

A2A message logs

Final consolidated responses
