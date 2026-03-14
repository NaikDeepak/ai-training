# AI Agent Mastery - Week 1 Learnings

This file contains key notes, concepts, and important debugging lessons from the AI Agent Mastery Week 1 training.

## 1. Agent Fundamentals
-   **AI Agent vs. Chatbot/Script:** Agents are autonomous systems that Observe, Decide (Think), and Act in loops, using tools and memory. Chatbots are typically single-turn text generators.
-   **Agent Loop:** Observe (input) -> Think (LLM reasons) -> Act (tool call or response).
-   **Levels of Autonomy:** From Rule-Based (Level 0) to Fully Autonomous (Level 4). Week 1 focused on Levels 2-3.

## 2. Environment Setup
-   **Google Colab:** Chosen for free GPU access and no local setup.
-   **API Keys:** **CRITICAL SECURITY PRACTICE:** ALWAYS use Colab Secrets (`userdata.get()`) or environment variables. NEVER hardcode API keys in notebooks or commit them to Git.
-   **Frameworks:** LangGraph & Google ADK.
-   **Observability:** Arize Phoenix for tracing agent executions (LLM calls, tool calls, full traces). Essential for debugging the "black box" problem.

## 3. LLM API Integration
-   Direct calls to OpenAI (`ChatOpenAI`) and Gemini (`ChatGoogleGenerativeAI`).
-   Understanding token costs is vital for managing expenses (`gpt-4o-mini` and Gemini Flash are cost-effective for learning).

## 4. Basic Tool Integration
-   **Purpose:** Tools allow agents to interact with the outside world (search, APIs, databases).
-   **Google ADK Tools:**
    -   Tools are defined as standard Python functions.
    -   Passed directly to `LlmAgent(tools=[my_function])`. ADK infers `name` (function name) and `description` (docstring).
    -   **Lesson Learned (Pollinations.ai):** External APIs change! Needed to adapt from direct URL to `/api/batches` with POST/GET/polling for asynchronous generation.
-   **LangGraph Tools:**
    -   Functions decorated with `@tool` from `langchain_core.tools`.
    -   Bound to the LLM using `llm.bind_tools(tools)`.
    -   Tools are executed via `ToolNode` in the graph.
    -   Graph flow (`add_conditional_edges`) decides when to call tools.

## 5. State Management & Memory
-   **LangGraph State:**
    -   Explicitly defined using `TypedDict` (`AgentState`).
    -   State is passed and updated between nodes in the graph.
    -   `Annotated[list, add_messages]` is key for automatic conversation history management.
-   **Google ADK Session State:**
    -   Managed automatically per session by `InMemorySessionService` and `LlmAgent`.
    -   The LLM's `instruction` prompt is crucial for guiding it to remember and utilize session-specific information (e.g., user's name).

## 6. Structured Output & Security Mindset
-   **Structured Output:**
    -   **JSON Mode:** Basic raw JSON from LLMs (`model_kwargs={"response_format": {"type": "json_object"}}`).
    -   **Pydantic Models (Recommended):** Type-safe schemas (`BaseModel`) integrated with LLMs via `llm.with_structured_output(MySchema)`. Ensures robust, validated output.
-   **Security Mindset:**
    -   Threats: Prompt Injection, Tool Misuse, Data Leakage, Credential Exposure.
    -   **Rule #1:** NEVER hardcode API keys. Use environment variables/secrets.
    -   Basic input validation is a starting point.

## 7. Hands-On Project Learnings (Topic Research Agent)
-   **Comparison:**
    -   **LangGraph:** More explicit control over multi-step workflows (nodes, edges). Requires more boilerplate but offers fine-grained orchestration.
    -   **ADK:** More concise for instruction-driven, often single-turn or simple multi-turn tasks. Relies heavily on prompt engineering for complex logic.
-   **Key Debugging Lessons & Solutions:**
    -   **`await app.ainvoke(...)`:** Always use the `async` version in Jupyter/Colab when `await`ing. (Initial `TypeError: object dict can't be used in 'await'`).
    -   **LangChain `NotImplementedError: Unsupported message type`:** Occurs when trying to put non-`BaseMessage` objects (like Pydantic instances) directly into `AgentState['messages']`. Solution: Remove `messages` from state if not directly for LLM conversation history, or ensure only `BaseMessage` types are added.
    -   **Interactive LangGraph Loops:**
        -   **Problem:** Initial infinite loop due to graph trying to re-execute without new user input.
        -   **Solution (Your Fix!):** Set graph edge to `workflow.add_edge("chat", END)`. The external `while True` Python loop handles user `input()`, feeds new `HumanMessage` data to `agent_memory_chat.ainvoke()` for each single turn, and manages loop termination (e.g., "quit", "exit"). This correctly separates graph execution from external human interaction.
    -   **External API Changes:** Be prepared to update tool implementations as external services evolve (e.g., Pollinations.ai requiring batch API).
    -   **Git Authentication (Manual):** For command-line `git push`, use a GitHub Personal Access Token (PAT) as the password when prompted in your local terminal. This is often necessary when direct browser login isn't available in the execution environment.

This comprehensive learning log will be a valuable reference for your AI Agent Mastery journey!