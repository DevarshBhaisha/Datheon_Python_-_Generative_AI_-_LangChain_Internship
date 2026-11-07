# Multi-Tool Autonomous AI Agent

A tool-using AI agent built with **Python, LangChain, and Google Gemini**. It can interpret user requests, select appropriate tools, execute multi-step workflows, and combine tool results into a natural-language response.

Unlike a basic chatbot that only generates text, this project demonstrates practical agent engineering through tool orchestration, controlled tool access, input validation, error handling, and automated testing.

## Key Features

- **Autonomous tool selection:** The LangChain agent decides which tools are relevant to a request.
- **Web search:** Uses DuckDuckGo to retrieve search results with titles, summaries, and URLs.
- **Safe calculator:** Evaluates mathematical expressions using Python's AST with an explicit operator and function allowlist. Does not use `eval()`.
- **Local file reader:** Reads supported text-based files from the project's `data/` directory.
- **Multi-step orchestration:** Combines multiple tools in one workflow.
- **Visible execution trace:** Displays tool actions and observations during agent execution.
- **Error handling:** Handles invalid inputs, tool failures, file-access violations, and agent execution errors.
- **Automated testing:** Includes tests for calculator behavior, file access, and web-search error handling.

## Architecture

```text
                   User Query
                       |
                       v
              Python CLI Interface
                       |
                       v
             LangChain Agent (Gemini)
                       |
              Autonomous Tool Selection
                       |
          +------------+------------+
          |            |            |
          v            v            v
       Web Search   Calculator   File Reader
       (DuckDuckGo)  (Safe AST)  (Local data/)
          |            |            |
          +------------+------------+
                       |
                       v
               Tool Observations
                       |
                       v
                 Gemini Agent
                       |
                       v
                Final Response
```

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| Agent framework | LangChain |
| LLM | Google Gemini |
| Web search | DuckDuckGo (`ddgs`) |
| Calculator | Python AST and math |
| Configuration | python-dotenv |
| Testing | pytest |

## Project Structure

```text
multi_tool_autonomous_ai_agent/
│
├── data/
│   ├── README.md
│   └── sample_notes.txt
│
├── tests/
│   └── test_tools.py
│
├── agent.py
├── main.py
├── tools.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup and Installation

### Prerequisites

- Python 3.10 or newer
- Google Gemini API key
- Internet connection for Gemini API calls and web search

### Windows PowerShell

```powershell
git clone <YOUR_REPOSITORY_URL>
cd multi_tool_autonomous_ai_agent

py -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt

Copy-Item .env.example .env
```

Open `.env` and configure your Gemini API key:

```env
GOOGLE_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
```

Keep your actual `.env` file private. Never commit API keys to GitHub.

### macOS / Linux

```bash
git clone <YOUR_REPOSITORY_URL>
cd multi_tool_autonomous_ai_agent

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt

cp .env.example .env
```

Add your Gemini API key to `.env`.

## Running the Agent

### Interactive mode

```bash
python main.py
```

Enter a request when prompted. Type `help` for instructions or `exit` to quit.

### Single-query mode

```bash
python main.py --query "Calculate 125 multiplied by 48."
```

## Multi-Step Workflow Examples

### Workflow 1: Local File → Calculator

**Request:** Read `sample_notes.txt`, identify the three approaches described, and calculate the number of unique pairwise comparisons.

**Execution:**
1. Agent selects the local file-reader tool.
2. Reads and interprets the file.
3. Identifies three approaches.
4. Selects the calculator tool.
5. Calculates `3 × 2 / 2 = 3`.
6. Combines the results into a final response.

### Workflow 2: Web Search → Calculator

**Request:** Find the official Python downloads page and calculate how many days are in 12 weeks.

**Execution:**
1. Agent selects DuckDuckGo search.
2. Retrieves the official Python downloads page.
3. Selects the calculator tool.
4. Calculates `12 × 7 = 84`.
5. Returns the URL and calculation together.

These workflows demonstrate that the agent can select and sequence tools based on the user's request rather than following a fixed execution sequence.

## Example Prompts

- "Search for the latest reported population of Japan, then calculate 2% of that number."
- "Read `sample_notes.txt` and summarize the main evaluation criteria."
- "Search for the current price of a product and calculate the total for seven units with 8% tax."
- "Read a local note, search for a claim that needs verification, and compare the findings."

Web search results may be incomplete or outdated. Verify important information independently.

## Testing

Run the automated test suite:

```powershell
python -m pytest -v
```

Current test coverage: **15 passing tests**.

Tests cover:

- Arithmetic operations and mathematical functions.
- Rejection of unsafe expressions and unsupported inputs.
- Division-by-zero and invalid mathematical operations.
- Expression-length limits.
- File reading and missing-file handling.
- Path traversal and absolute-path protection.
- Unsupported file types and oversized files.
- Empty web-search queries.
- Web-search provider failures.

Tests use controlled inputs and mocked provider failures; they do not require live Gemini API calls or real web searches.

## Security and Reliability

- **Restricted calculator:** Uses AST parsing and an explicit allowlist instead of executing arbitrary Python code.
- **Controlled file access:** Resolves file paths and rejects paths outside the designated `data/` directory.
- **Read-only tools:** The agent cannot write, modify, delete, or execute local files through its available tools.
- **File restrictions:** Limits supported extensions and file size.
- **Configuration protection:** Loads credentials from environment variables and keeps `.env` out of source control.
- **Failure handling:** Tool and agent errors are handled without treating failed operations as successful results.

The agent is an experimental assistant, not an authoritative source of information. Its responses should be independently verified when accuracy is important.

## Future Enhancements

- LangSmith tracing and agent-performance evaluation.
- Structured JSON output and schema validation.
- More comprehensive model and integration tests.
- A Streamlit interface for interactive conversations and tool traces.
- Retrieval-augmented generation (RAG) for larger document collections.
- Improved tool-call deduplication and execution limits.

## Project Objective

This project demonstrates practical AI engineering concepts, including LLM integration, agent architecture, tool calling, multi-step orchestration, input validation, safe execution boundaries, failure handling, and automated testing.