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
├── crewai_mod/       # CrewAI implementation
├── langgraph_mod/    # LangGraph implementation
├── autogen_mod/      # AutoGen implementation
├── agno_mod/         # Agno implementation
├── adk_mod/          # ADK implementation
├── requirements.txt
├── .env.example
└──  README.md
└──  start.py

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
uv run agno_mod/main.py
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

### 1) General

| Feature                | **CrewAI**                 | **LangGraph**                | **AutoGen**                    | **Agno**                         | **ADK**                         |
|------------------------|----------------------------|------------------------------|--------------------------------|-----------------------------------|----------------------------------|
| **Orchestration**      | Sequential pipeline        | State graph (DAG)            | Group chat (multi-agent)       | Declarative agent workflow        | Declarative modular pipeline     |
| **Agent Roles**        | Explicit agents + tasks    | Nodes as agents/tools        | Conversation-driven agents     | Role-based modular agents         | Explicit agents + tools          |
| **Task Flow**          | Linear, step-by-step       | Dynamic transitions, loops   | Multi-turn collaborative chat  | Sequential or parallel pipelines  | Sequential pipeline              |
| **Extensibility**      | Add agents / tasks easily  | Add nodes, edges, memory     | Add agents, tools, chat rules  | Add agents, skills, providers     | Add agents, tools, adapters      |
| **Best For**           | Business workflows         | Complex dependency graphs     | Dynamic team collaboration     | Product-ready agent workflows     | Lightweight agent pipelines      |
| **Learning Curve**     | Low/Medium                 | Medium/High                  | Medium                         | Low/Medium                        | Low                              |
| **Output Style**       | Executive report           | Analysis w/ structured steps | Chat log + synthesized report  | Structured final output           | Structured final output          |

### 2) Architecture & Execution model

| Dimension                        | CrewAI                              | LangGraph                              | AutoGen                                  | Agno                                  | ADK                                    |
|----------------------------------|--------------------------------------|------------------------------------------|-------------------------------------------|----------------------------------------|------------------------------------------|
| **Execution Model**              | Task list + agent executor           | Graph-based state machine / DAG          | Conversational multi-agent runtime        | Declarative pipeline (Agents + Tools)   | Declarative pipeline DSL                |
| **Supports branching?**          | ❌ Non                                | ✅ Oui (if/else, loops, recursion)        | Limited (via agent messages)              | Partiel (via functions)                | ❌ Non                                   |
| **Supports parallelism?**        | ❌ Pas natif                           | ✅ Oui                                    | Possible via async agents                 | Oui (async providers)                  | Non                                     |
| **Memory system**                | Basic (context injection)             | Advanced (Graph memory, checkpoints)     | Chat history + external memory options     | Optional memory                        | Minimal                                 |
| **Recoverability / Resume**      | ❌ Non                                | ✅ Oui (checkpointing)                    | Partiel (depends on orchestration)         | Oui (depends on implementation)        | Non                                     |


### 3) Agents & Skills

| Feature                       | CrewAI                                  | LangGraph                            | AutoGen                          | Agno                                        | ADK                              |
|------------------------------|------------------------------------------|----------------------------------------|----------------------------------|----------------------------------------------|----------------------------------|
| **Custom agent roles**       | Oui, explicites                          | Oui, via nodes                         | Oui, via conversational roles    | Oui, rôles + skills + tools                 | Oui                               |
| **Tool Use / Function Calling** | Oui, facile                               | Oui, très avancé                        | Oui                             | Oui, modèle "providers" + tools             | Oui, simple                        |
| **Skill Libraries**          | Oui (bientôt standardisées)               | Pas natif                               | Non standard                     | Oui (skills, plugins)                        | Faible                            |
| **Concurrency**              | Non                                       | Oui                                     | Oui (multi-agent simultané)      | Oui                                         | Non                               |


### 4) Use Cases / Ideals domains

| Cas d’usage                     | CrewAI                                  | LangGraph                                 | AutoGen                               | Agno                                          | ADK                                   |
|----------------------------------|------------------------------------------|---------------------------------------------|----------------------------------------|------------------------------------------------|----------------------------------------|
| Workflows d’entreprise           | ⭐⭐⭐⭐⭐                                     | ⭐⭐⭐⭐                                       | ⭐⭐⭐                                     | ⭐⭐⭐⭐⭐                                         | ⭐⭐⭐⭐                                  |
| Graphes complexes                | ⭐⭐                                        | ⭐⭐⭐⭐⭐ (best choice)                         | ⭐⭐                                      | ⭐⭐⭐                                          | ⭐⭐                                     |
| Agents collaboratifs interactifs | ⭐⭐                                        | ⭐⭐⭐⭐                                       | ⭐⭐⭐⭐⭐ (best choice)                     | ⭐⭐⭐                                          | ⭐⭐                                     |
| Pipelines ML / AI robustes       | ⭐⭐⭐                                      | ⭐⭐⭐⭐⭐                                       | ⭐⭐⭐⭐                                   | ⭐⭐⭐⭐⭐                                         | ⭐⭐⭐⭐                                  |
| Rapports financiers               | ⭐⭐⭐⭐⭐                                     | ⭐⭐⭐⭐                                       | ⭐⭐⭐⭐                                   | ⭐⭐⭐⭐⭐                                         | ⭐⭐⭐⭐                                  |


### 5) Benefits and limits

**CrewAI**
+ Very easy to use
+ Ideal for business workflows
+ Highly readable agents
- No complex graphs
- No advanced state logic

**LangGraph**
+ Most powerful for complex workflows
+ Supports loops, branches, memory
+ Ideal for RAG, ML pipelines, persistent agents
- Harder to learn
- Quite verbose

**AutoGen**
+ Highly interactive agents
+ Unique 'Group Chat' mode
+ Flexible, adaptable
- Less structured for linear workflows
- Can become verbose

**Agno**
+ Very clean, very modern
+ Agents + skills + providers (Tavily, SQL, YFinance)
+ Perfect for building complete 'AI Apps'
- Community still growing
- Less academic than LangGraph

**ADK**
+ Minimalist, quick to deploy
+ Simple for fixed pipelines
+ Perfect for POCs
- Less feature-rich
- Not designed for complex workflows



---

## 📚 Further Reading
- [CrewAI Documentation](https://docs.crewai.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [AutoGen Documentation](https://microsoft.github.io/autogen/)
- [Agno Documentation](https://docs.agno.com/)
- [Google ADK Documentation](hhttps://google.github.io/adk-docs/)

---

**This project is a reference for anyone looking to build modular, multi-agent systems in Python using modern frameworks.**

