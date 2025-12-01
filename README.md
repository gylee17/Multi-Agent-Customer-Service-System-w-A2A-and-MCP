# Multi-Agent Customer Service System (A2A + MCP + LangGraph)

This project implements a **multi-agent customer service automation system** using:

- **Agent-to-Agent (A2A) communication with LangGraph**
- **LLM-powered agents** (Router, Data, Support)
- **Model Context Protocol (MCP) server for customer + ticket data**
- **SQLite customer database with tools exposed via MCP**
- **Three interacting LLM agents coordinating to solve customer queries**

The system demonstrates:

- Intelligent **task allocation**
- Multi-agent **negotiation & escalation**
- Multi-step **coordinated problem solving**
- Retrieval, updates, and ticket creation via **MCP tools**

---

# 1. Project Structure

Below is the exact project layout in this repository:

```text
.
├── agents/
│   ├── base.py                  # Base message schema + common utilities
│   ├── router_agent.py          # LLM Router agent (intent detection + coordination)
│   ├── data_agent.py            # LLM Data agent (talks to MCP tools)
│   └── support_agent.py         # LLM Support agent (resolution, escalation)
│
├── demo/
│   └── run_scenarios_langgraph.py   # MAIN end-to-end LangGraph A2A demo
│
├── mcp_server/
│   ├── database_setup.py        # Creates support.db + sample data
│   ├── db.py                    # SQLite connection helper
│   └── tools.py                 # MCP tool implementations:
│                                #   - get_customer
│                                #   - list_customers
│                                #   - update_customer
│                                #   - create_ticket
│                                #   - get_customer_history
│
├── requirements.txt             # Dependency list (LangGraph, LangChain, OpenAI, etc.)
└── README.md
```

---

# 2. Requirements

This project uses:

- **LangGraph**
- **LangChain OpenAI**
- **OpenAI API**
- **SQLite**
- **Python standard library**

Your `requirements.txt` includes:

```text
langgraph>=0.0.30
langchain-openai>=0.1.0
openai>=1.13.0
tiktoken>=0.7.0
python-dotenv>=1.0.1
sqlite3-bro==0.0.1
```

---

# 3. Setup Instructions

Follow these steps EXACTLY to run the full system.

---

## 3.1 Clone the Repository

```bash
git clone https://github.com/<your-username>/Multi-Agent-Customer-Service-System-w-A2A-and-MCP.git
cd Multi-Agent-Customer-Service-System-w-A2A-and-MCP
```

---

## 3.2 Create & Activate Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate      # macOS / Linux
# Windows:
# .venv\Scripts\activate
```

You should now see `(.venv)` in your terminal.

---

## 3.3 Install Requirements

```bash
pip install -r requirements.txt
```

---

## 3.4 Set OpenAI API Key

```bash
export OPENAI_API_KEY="your-key-here"
```

Or create a `.env`:

```
OPENAI_API_KEY=your-key-here
```

---

## 3.5 Initialize the MCP Database

```bash
cd mcp_server
python database_setup.py
```

When prompted:

```
Would you like to insert sample data? (y/n): y
```

Verify:

```bash
ls
# support.db should be visible
```

Return to repo root:

```bash
cd ..
```

---

# 4. Running the Multi-Agent A2A System

Run the LangGraph-powered end-to-end demo:

```bash
python demo/run_scenarios_langgraph.py
```

This will output:

- Scenario title  
- Input user query  
- LLM Router → Data Agent → Support Agent message exchanges  
- MCP tool calls (get_customer, list_customers, update_customer…)  
- Final natural language answer  

---

# 5. Test Scenarios Implemented

The system covers all required queries in the assignment:

### ✔ Simple Query  
**“Get customer information for ID 5”**  
→ Router → Data Agent → MCP → Return profile

---

### ✔ Task Allocation  
**“I need help with my account, customer ID 12345”**  
→ Router detects support intent  
→ Data Agent fetches customer info  
→ Support finalizes the response

---

### ✔ Negotiation / Escalation  
**“I want to cancel my subscription but I’m having billing issues”**  
→ Multiple competing intents  
→ Support ↔ Router ↔ Data Agent negotiation  
→ Coordinated answer

---

### ✔ Multi-Step Coordination  
**“What’s the status of all high-priority tickets for premium customers?”**  
→ Router decomposes  
→ Data Agent fetches premium customers  
→ Support Agent fetches high-priority tickets  
→ Router synthesizes results

---

### ✔ Complex Query  
**“Show me all active customers who have open tickets”**

---

### ✔ Escalation  
**“I’ve been charged twice, please refund immediately!”**  
→ Router detects urgency  
→ Support Agent escalates

---

### ✔ Multi-Intent  
**“Update my email to new@email.com and show my ticket history”**  
→ Data Agent updates email via MCP  
→ Data Agent retrieves ticket history  
→ Support Agent formats final answer

---

# 6. Notebook Demo (Optional)

A Colab-ready notebook (recommended by instructor) is available in:

```
demo/run_scenarios_langgraph.ipynb
```

It demonstrates:

- System initialization  
- MCP tool tests  
- Agent prompts  
- LangGraph routing  
- Full A2A logs  

---

# 7. Conclusion

This project demonstrates how **LLM-based agents**, MCP tools, and LangGraph routing can work together to automate customer service workflows. Building the MCP server, designing task-specific prompts, and ensuring proper A2A communication provided hands-on experience with real multi-agent architectures used in industry settings. The challenges mainly involved correctly handling agent state, preventing mis-routing, and ensuring tool responses aligned with agent expectations, all of which strengthened practical understanding of multi-agent coordination.

