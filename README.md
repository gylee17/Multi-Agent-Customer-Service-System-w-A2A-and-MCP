# Multi-Agent Customer Support System (Google ADK + MCP + SQLite)

This project implements an end-to-end **multi-agent customer support system** using:

- **Google Agent Development Kit (ADK)** for multi-agent orchestration  
- **A Model Context Protocol (MCP) HTTP server** exposing database tools  
- **SQLite database** for customer + ticket data (`support.db`)  
- **Ngrok** to make the MCP server publicly reachable from ADK  
- **Three conceptual agents**:
  - **Router Agent** – understands intent and routes the request  
  - **Customer Data Agent** – calls MCP tools to read/update the DB  
  - **Support Agent** – handles billing issues, upgrades, and escalation  

The system walks through realistic customer-support scenarios such as:
- Fetching a customer profile  
- Upgrading accounts  
- Finding active customers with open tickets  
- Handling duplicate billing and refunds  
- Updating contact info and summarizing ticket history  

---

## 1. Project Files

This repository has a **flat structure** (created from Colab):

```text
.
├── README.md               # This file
├── requirements.txt        # Python dependencies
├── database_setup.py       # Script to create and seed support.db
├── mcp_server.ipynb        # Colab/Jupyter notebook: MCP server + ngrok tunnel
└── a2a.ipynb               # Colab/Jupyter notebook: ADK multi-agent demo
```

### What each file does

- **`database_setup.py`**

  - Creates `support.db` (SQLite database).

  - Builds `customers` and `tickets` tables.

  - Optionally inserts sample customers + tickets used in the demo.

- **`mcp_server.ipynb`**

  - Defines low-level SQLite helpers (`get_db_connection`, `row_to_dict`, etc.).

  - Implements Python functions:

    - `get_customer`

    - `list_customers`

    - `update_customer`

    - `create_ticket`

    - `get_customer_history`

  - Wraps these functions as **MCP tools**.

  - Starts a **Flask HTTP server** with an `/mcp` endpoint that speaks MCP over Server-Sent Events (SSE).

  - Uses **ngrok** to expose the local server as
    `https://<random-subdomain>.ngrok-free.dev/mcp`.

  - Includes a test cell that sends an `initialize` MCP request via `requests` and prints the server’s response.

- **`a2a.ipynb`**

  - Configures the **MCPToolset** in Google ADK pointing at the MCP URL.

  - Defines the **Customer Data Agent** (`LlmAgent`) that uses the MCP tools.

  - Defines the **Router Agent** and **Support Agent** plus helper functions like `ask_agent_team(...)`.

  - Runs the assignment’s demo scenarios (customer lookup, upgrade help, open tickets, billing issue, email update +
    history).

  - Prints a detailed **Agent Event Trace** for each scenario.

## 2. Requirements

All Python dependencies are listed in `requirements.txt`.
Typical libraries include:

  - `google-adk` (Agent Development Kit)

  - `a2a` (Agent-to-Agent protocol)

  - `flask`, `flask-cors`

  - `requests`, `python-dotenv`, `termcolor`, `pyngrok`

  - Standard Python libraries (already included in Python runtime)

Install them after creating a virtual environment (see below).

## 3. Setup & Installation

You can run this project **locally** (recommended for the README) or entirely in **Colab** (as originally developed).

### 3.1 Clone the Repository
``` text
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```

### 3.2 Create & Activate a Virtual Environment
``` text
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
```

### 3.3 Install Requirements
``` text
pip install -r requirements.txt
```

### 3.4 Set Your OpenAI API Key

You can either export it:

``` text
export OPENAI_API_KEY="your-openai-key-here"
```

or create a `.env` file in the repo root:

``` text
OPENAI_API_KEY=your-openai-key-here
```

## 4. Step 1 – Initialize the SQLite Database

Run the setup script from the repository root:

``` text
python database_setup.py
```

When prompted:

``` text
Would you like to insert sample data? (y/n): y
```

This will create a `support.db` file in the same directory with:

  - A `customers` table (id, name, email, phone, status, timestamps)

  - A `tickets` table (id, customer_id, issue, status, priority, created_at)

  - Sample customers and ticket history used in the demo scenarios

You can verify it exists with:

``` text
ls
# You should see: database_setup.py, a2a.ipynb, mcp_server.ipynb, support.db, etc.
```

## 5. Step 2 – Run the MCP Server Notebook

The MCP server runs inside `mcp_server.ipynb`.

### 5.1 Open the Notebook

You can open it in:

  - **Colab** (upload the repo / sync from GitHub), or

  - **Jupyter / VS Code** locally.

### 5.2 Run the Cells in Order

In `mcp_server.ipynb`:

  **1. Imports & configuration**

    - `sqlite3`, `flask`, `flask_cors`, `requests`, `termcolor`, `pyngrok`, etc.

    - `DB_PATH = "./support.db"` (must match the database created in Step 1).

  **2. Database helper functions**

    - `get_db_connection()`

    - `row_to_dict(row)`

  **3. Business logic functions** (direct SQLite access):

    - `get_customer(customer_id: int)`

    - `list_customers(status: Optional[str] = None)`

    - `update_customer(customer_id, name, email, phone)`

    - `create_ticket(customer_id, issue, priority)`

    - `get_customer_history(customer_id)`

  **4. MCP server implementation**

    - Defines MCP tools (`MCP_TOOLS`) with JSON schemas.

    - Implements handlers for:

      - `"initialize"`

      - `"tools/list"`

      - `"tools/call"`

    - Exposes `/mcp` (POST) for MCP messages using SSE.

  **5. Flask + ngrok startup**

    - Starts Flask on `127.0.0.1:5000`.

    - Runs a health check (`/health`).

    - Authenticates ngrok using `NGROK_AUTHTOKEN`.

    - Prints lines like:

      ``` text
      ✅ MCP Server is running!
      📍 Local URL: http://127.0.0.1:5000
      
      🌐 Setting up public tunnel with ngrok...
      ✅ Public URL: https://una-verminous-chace.ngrok-free.dev
      🔗 MCP ENDPOINT : https://una-verminous-chace.ngrok-free.dev/mcp
      ```

    - **Copy the MCP endpoint URL** — you will need it in `a2a.ipynb`.

## 6. MCP self-test cell (optional but recommended)

  - Sends an `"initialize"` JSON-RPC request with `requests.post`.

  - Streams the SSE response and prints:

      ``` text
      ✅ Got MCP response from ADK notebook:
      {
        "jsonrpc": "2.0",
        "id": 999,
        "result": {
          "protocolVersion": "2024-11-05",
          "capabilities": { "tools": {} },
          "serverInfo": { "name": "customer-management-server", "version": "1.0.0" }
        }
      }
      ```

If you see this, your **MCP server + ngrok tunnel are working**.


## 6. Step 3 – Run the Multi-Agent A2A Notebook

Open `a2a.ipynb`.

### 6.1 Configure MCP Toolset

Make sure the cell that defines `MCP_SERVER_URL` uses the tunnel from the previous step. Example:

``` text
MCP_SERVER_URL = "https://una-verminous-chace.ngrok-free.dev/mcp"
```

Then the customer data agent is wired like:

``` text
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams

customer_data_mcp_tools = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=MCP_SERVER_URL
    )
)

customer_data_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="customer_data_agent",
    description="Agent focused on reading and updating customer records via MCP tools.",
    tools=[customer_data_mcp_tools],
    instruction="""
You are a customer data specialist.

You can reach a customer database through MCP tools. Use them to:
- fetch details for specific customers by ID
- list customers (optionally by status)
- update contact information (name, email, phone)
- review support ticket history
- open new support tickets

When you act:
- Call the appropriate MCP tool.
- Explain briefly what you did.
- Present customer information in a clean, readable format.
"""
)
```

### 6.2 Router & Support Agents

`a2a.ipynb` also defines:

- A **router agent** that:

  - Reads the user query

  - Decides whether this is primarily data, support, or mixed

  - Calls `transfer_to_agent` to delegate work to `customer_data_agent` or `support_agent`.

- A **support agent** that:

  - Handles billing issues, refunds, and account changes

  - May ask the data agent for customer or ticket context

  - Returns a user-friendly explanation in natural language.

### 6.3 Running the Demo Scenarios

Near the end of `a2a.ipynb`, there is:

``` text
async def run_demo_scenarios():
    await ask_agent_team("Please pull the customer record for ID 5.")
    await ask_agent_team("I'm customer 12345 and I'd like to upgrade my account. What should I do?")
    await ask_agent_team("Show me which active customers currently have open support tickets.")
    await ask_agent_team("I was billed twice on my last invoice. I need this investigated and refunded as soon as possible.")
    await ask_agent_team("For customer 1, update the email address to new@email.com and then summarize their recent ticket history.")

await run_demo_scenarios()
```

Running this cell prints, for each query:

- A **header** with the user message

- An **Agent Event Trace** showing:

  - Router delegation

  - MCP tool calls (e.g., `get_customer`, `get_customer_history`)

  - Tool results (success or errors like “no such table” if DB is missing)

  - Final answer returned back to the “user”.

When `support.db` exists and MCP is wired correctly, the system will:

  - Pull customer 5

  - Attempt an upgrade flow for customer 12345

  - Show active customers with open tickets

  - Acknowledge double billing and promise investigation + refund

  - Update customer 1’s email and summarize their ticket history.


## 7. Typical Issues & Debugging Notes

During development, the following were common pitfalls:

**1.** `no such table: customers`

  - Cause: `support.db` not created or `database_setup.py` not run in the same directory as `mcp_server.ipynb`.

  - Fix: Re-run `python database_setup.py` and confirm `support.db` exists next to the notebook.

**2. Server timeouts or** `No response received`

  - Cause: MCP server not running, ngrok tunnel expired, or MCP URL mismatched.

  - Fix: Restart `mcp_server.ipynb`, copy the fresh ngrok `/mcp` URL, and update `MCP_SERVER_URL` in `a2a.ipynb`.

**3. Port 5000 already in use**

  - Cause: A previous Flask server still running in Colab/locally.

  - Fix: Restart the runtime or change the port used in `server.py` / `mcp_server.ipynb`.

Understanding these failure modes was part of the learning experience and helped reinforce how brittle multi-component systems can be when any link (DB, tunnel, or URL) is misconfigured.
