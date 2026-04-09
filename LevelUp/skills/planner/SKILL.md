---
name: LevelUp-Planner-Agent
description: Generates a 7-day structured learning plan based on user goals, time, and skill level. Designed to be spawned by the main OpenClaw agent for plan generation requests.
allowed-tools: Bash(python3:*), Bash(pip:*), Bash(uv:*)
---

# LevelUp Planner Agent Skill

This agent is responsible for creating a structured 7-day learning roadmap.

## Input:

The agent expects a single string input (passed as the `task` argument to `sessions_spawn`) containing a JSON-formatted string with the following keys:

```json
{
  "user_goal": "string",
  "time_per_day_minutes": "int",
  "skill_level": "string"
}
```

## Output:

The agent will print a JSON-formatted string to stdout representing the generated 7-day learning plan, following the structure below:

```json
{
  "day_1": {
    "theme": "string",
    "tasks": [
      {"type": "learn", "title": "string", "duration": "string"},
      {"type": "apply", "title": "string", "duration": "string"},
      {"type": "reflect", "question": "string"}
    ]
  },
  // ... up to day_7
}
```

## Invocation:

This agent is intended to be spawned by the main OpenClaw agent using `sessions_spawn` with `runtime="subagent"` and the input JSON passed as the `task` argument.

Example (from orchestrator): 

```python
default_api.sessions_spawn(
    runtime="subagent",
    agentId="LevelUp-Planner-Agent", # Matches skill name
    task=json.dumps(planner_input_data), # JSON string of input
    mode="run",
    cleanup="delete",
    model="google/gemini-3.1-pro-preview",
    # ... (other parameters if needed)
)
```

## Internal Implementation (`planner_agent.py`):

The `planner_agent.py` script will be executed. It should:
1. Read the input JSON string from standard input (or the `task` argument, depending on how `sessions_spawn` delivers it).
2. Parse the input.
3. Use the Google ADK (e.g., Gemini model) to generate the plan.
4. Print the resulting plan JSON to `stdout`.
