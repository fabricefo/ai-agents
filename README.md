# AI Agent Frameworks Comparison: CrewAI vs LangGraph vs AutoGen vs Agno vs Google ADK

This project demonstrates and compares three leading Python agent frameworks for orchestrating multi-agent financial analysis workflows:

- **CrewAI**: Role-based, sequential agent orchestration
- **LangGraph**: State-driven, graph-based agent workflows
- **AutoGen**: Conversational, group-chat style agent collaboration
- **Google ADK**
- **Agno**

All frameworks are implemented to solve the same problem: **analyzing a stock's recent performance and generating an investment recommendation (BUY/SELL/HOLD) with rationale**.

## 📦 Project Structure

```
ai-agent-comparision/
├── crewai/       # CrewAI implementation
├── langgraph/    # LangGraph implementation
├── autogen/      # AutoGen implementation
├── agno/         # Agno implementation
├── adk/          # ADK implementation
├── requirements.txt
├── .env.example
└──  README.md

```

---

## 🚀 How to Use & Run Each Framework

### 1. Prerequisites
- Python 3.8+
- API keys for [OpenAI](https://openai.com/fr-FR/api/) and [Tavily](https://tavily.com/)
- Install dependencies:
  ```bash
  uv venv
  uv pip install -r requirements.txt
  cp .env.example .env  # and fill in your API keys
  ```

### 2. Running Each Implementation

#### CrewAI
```bash
uv run crewai_mod/main.py
```
- **Prompt:** Enter a stock ticker (e.g. NVDA, AAPL)
- **Output:** Executive summary and recommendation

#### LangGraph
```bash
uv run langgraph_mod/main.py
```
- **Prompt:** Enter a stock ticker
- **Output:** Analysis and recommendation

#### AutoGen
```bash
uv run autogen_mod/main.py
```
- **Prompt:** Enter a stock ticker
- **Output:** Analyst/Researcher group chat, final report

#### Agno
```bash
uv run agon_mod/main.py
```
- **Prompt:** Enter a stock ticker
- **Output:** Analyst/Researcher group chat, final report
  
---

### 3. Running All Implementations

```bash
uv run start.py
```

### 4. Docker

Build : ```docker-compose build```
Run : ```docker-compose run stock-analysis```


## 🧩 Framework Comparison Table

| Feature                | CrewAI                | LangGraph                | AutoGen                  |
|------------------------|----------------------|--------------------------|--------------------------|
| **Orchestration**      | Sequential pipeline  | State graph (DAG)        | Group chat (conversational) |
| **Agent Roles**        | Explicit, role-based | Node-based, flexible     | Conversational, flexible |
| **Task Flow**          | Linear, step-by-step | Custom graph transitions | Multi-turn dialogue      |
| **Extensibility**      | Add agents/tasks     | Add nodes/edges          | Add agents, chat logic   |
| **Best For**           | Business workflows   | Complex dependencies     | Dynamic collaboration    |
| **Code Structure**     | agents.py, tasks.py, tools.py | nodes.py, state.py, tools.py | agents.py, workflow.py, config.py |
| **Learning Curve**     | Low/Medium           | Medium/High              | Medium                   |
| **Output**             | Executive report     | Analysis + recommendation| Chat log + report        |


---

## 📚 Further Reading
- [CrewAI Documentation](https://docs.crewai.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [AutoGen Documentation](https://microsoft.github.io/autogen/)

---

**This project is a reference for anyone looking to build modular, multi-agent systems in Python using modern frameworks.**

Original source : https://github.com/Vigneshmaradiya/ai-agent-comparison/