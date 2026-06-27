# ⚡ Multi-Agent AI Research Assistant

A multi-agent AI research system that autonomously plans research, performs real-time web search, generates structured reports, critiques its own output, and iteratively refines the report until it reaches a target quality score.

The system follows a modular agent architecture consisting of four specialized agents:

* **Planner Agent** – Breaks a research query into focused research tasks.
* **Researcher Agent** – Retrieves relevant information from the web using the Tavily Search API.
* **Editor Agent** – Produces a structured research report and revises it using critic feedback.
* **Critic Agent** – Evaluates the report and suggests improvements using structured LLM output.

---

## Features

* Multi-agent architecture
* Automatic task decomposition
* Real-time web research
* Structured report generation
* AI-powered report evaluation
* Iterative self-improvement loop
* Streamlit web interface
* Structured output using Pydantic

---

# Architecture

```text
                     User Query
                          │
                          ▼
                  Planner Agent
                          │
          Generates 3 Research Tasks
                          │
                          ▼
               Researcher Agent(s)
                          │
        Tavily Advanced Web Search
                          │
                          ▼
             Combined Research Notes
                          │
                          ▼
                   Editor Agent
                          │
              Initial Research Report
                          │
                          ▼
                   Critic Agent
                          │
         Structured Evaluation (Score +
              Improvement Suggestions)
                          │
               Score >= Target ?
                 ┌────────┴────────┐
                 │                 │
                Yes               No
                 │                 │
                 ▼                 ▼
          Final Report      Editor Revises Report
                                   │
                                   └──────────────► Critic
```

---

# Tech Stack

* Python
* Streamlit
* LangChain
* Groq API (Llama 3.3 70B Versatile)
* Tavily Search API
* Pydantic
* Python Dotenv

---

# Project Structure

```text
multi-agent-ai-research-assistant/

│
├── agents/
│   ├── planner.py
│   ├── researcher.py
│   ├── editor.py
│   └── critic.py
│
├── app.py
├── pipeline.py
├── requirements.txt
├── .env.example
└── README.md
```

---

# How It Works

## 1. Planner Agent

The Planner Agent receives the user's query and decomposes it into **three focused research tasks**.

Example

**Input**

```
Future of Quantum Computing
```

**Output**

```
• Current state of quantum hardware

• Commercial applications

• Challenges and future outlook
```

---

## 2. Researcher Agent

Each task is independently researched using the **Tavily Search API** with advanced search enabled.

The retrieved information is combined into a single research context.

---

## 3. Editor Agent

The Editor Agent transforms the collected research into a well-structured report.

During later iterations, it also receives feedback from the Critic Agent and revises the report accordingly.

---

## 4. Critic Agent

The Critic Agent evaluates the report using a structured Pydantic schema.

Evaluation criteria include:

* Accuracy
* Completeness
* Structure
* Clarity
* Depth of analysis
* Supporting evidence
* Coverage of multiple perspectives
* Recent information
* Actionable insights

It returns:

* Quality score
* List of improvement suggestions

---

## 5. Iterative Refinement

If the report score is below the configured threshold, the report is revised.

This process repeats until:

* the target score is reached, or
* the maximum number of iterations is exceeded.

---

# Installation

Clone the repository

```bash
git clone https://github.com/vikas12900/multi-agent-ai-research-assistant.git

cd multi-agent-ai-research-assistant
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create a `.env` file

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Run the application

```bash
streamlit run app.py
```

---

# Example Workflow

1. Enter a research topic.
2. Planner Agent generates three research tasks.
3. Researcher Agent gathers information from the web.
4. Editor Agent writes the first draft.
5. Critic Agent evaluates the report.
6. If required, the Editor revises the report using the critic's suggestions.
7. The final report and evaluation history are displayed.

---

# Example Output

The application displays:

* Generated research tasks
* Critic evaluation history
* Final quality score
* Final research report
* Raw research collected from Tavily

---

# Future Improvements

* Parallel execution of research tasks
* Citation generation
* PDF report export
* Source credibility ranking
* Multi-model support
* Long-term memory
* Report version comparison

---
