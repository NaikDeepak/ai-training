import json
import time
from pathlib import Path
import re
import sys
import subprocess

# Assuming OpenClaw default_api is available in the execution environment
# and can call sessions_spawn, default_api.read, default_api.exec, default_api.write
# For this script to be run by OpenClaw itself, these would be accessible.

DATA_DIR = Path(__file__).parent / "data"
PLANNER_AGENT_ID = "LevelUp-Planner-Agent"

def load_json_data(filepath: Path):
    if not filepath.exists():
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json_data(filepath: Path, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def orchestrate_planner_agent():
    print("Orchestrator: Checking for planner trigger files...")
    trigger_files = list(DATA_DIR.glob("planner_trigger_*.json"))

    if not trigger_files:
        print("Orchestrator: No planner trigger files found.")
        return

    for trigger_file in trigger_files:
        print(f"Orchestrator: Found trigger file: {trigger_file.name}")
        try:
            request_data = load_json_data(trigger_file)
            if not request_data:
                print(f"Orchestrator: Failed to read {trigger_file.name}, skipping.")
                continue

            # Extract request_id from filename
            match = re.search(r"planner_trigger_(.*?)\.json", trigger_file.name)
            if not match:
                print(f"Orchestrator: Could not extract request_id from {trigger_file.name}, skipping.")
                continue
            request_id = match.group(1)
            plan_id = request_id # For now, plan_id is the same as request_id

            # Delete the trigger file immediately to avoid reprocessing
            trigger_file.unlink()
            print(f"Orchestrator: Deleted trigger file: {trigger_file.name}")

            user_goal = request_data.get("user_goal", "Unknown Goal")
            time_per_day_minutes = request_data.get("time_per_day_minutes", 60)
            skill_level = request_data.get("skill_level", "intermediate")

            planner_task_input = {
                "user_goal": user_goal,
                "time_per_day_minutes": time_per_day_minutes,
                "skill_level": skill_level,
            }
            planner_task_str = json.dumps(planner_task_input)

            print(f"Orchestrator: Spawning Planner Agent for request_id: {request_id}")
            
            # OpenClaw tool call for sessions_spawn
            # We need to ensure that the calling context (me) has access to default_api
            # and that sessions_spawn can be directly invoked.
            # For this to work seamlessly in a background process, the process itself needs tool access.
            # I will assume `default_api.sessions_spawn` is callable in this script's environment.
            
            # The output from sessions_spawn will contain the sub-agent's stdout as a string
            # in the 'output' field of the tool response.
            # It will also have a 'message' field with agent's reply.
            
            # In a real environment, the orchestrator.py might be part of an OpenClaw skill itself
            # or invoked in a way that provides tool access. For now, I'm simulating this.
            
            # For testing, I'll directly call the planner_agent.py script to get its output
            # instead of sessions_spawn, to bypass potential complexities with tool access in a background script.
            # THIS IS A TEMPORARY MOCK TO TEST THE ORCHESTRATION FLOW.
            # The actual sessions_spawn would look like:
            # response = default_api.sessions_spawn(
            #    runtime="subagent",
            #    agentId=PLANNER_AGENT_ID,
            #    task=planner_task_str,
            #    mode="run",
            #    cleanup="delete",
            #    model="google/gemini-3.1-pro-preview",
            # )
            # agent_output = response.get("output", "{}")
            
            # TEMPORARY MOCK: Directly run the planner_agent.py script
            planner_agent_script_path = Path(__file__).parent / "skills" / "planner" / "planner_agent.py"
            import subprocess
            process = subprocess.run([sys.executable, str(planner_agent_script_path), planner_task_str], capture_output=True, text=True)
            agent_stdout = process.stdout
            agent_stderr = process.stderr

            if process.returncode != 0:
                print(f"Orchestrator: Planner Agent failed for {request_id}. Error: {agent_stderr}", file=sys.stderr)
                # Handle error: maybe create a failed status file
                continue

            generated_plan = json.loads(agent_stdout)
            print(f"Orchestrator: Planner Agent generated plan for request_id: {request_id}")

            # Save the generated plan
            plan_filepath = DATA_DIR / f"plan_{plan_id}.json"
            save_json_data(plan_filepath.name, generated_plan)
            print(f"Orchestrator: Saved plan to {plan_filepath.name}")

            # Initialize history for this plan
            history_filepath = DATA_DIR / f"history_{plan_id}.json"
            initial_history = {"plan_id": plan_id, "completed_tasks": [], "missed_tasks": []}
            save_json_data(history_filepath.name, initial_history)
            print(f"Orchestrator: Initialized history to {history_filepath.name}")

            # Optionally, create a success status file for the frontend to poll
            status_filepath = DATA_DIR / f"planner_status_{request_id}_SUCCESS.json"
            save_json_data(status_filepath.name, {"plan_id": plan_id, "status": "completed", "timestamp": time.time()})
            print(f"Orchestrator: Wrote status file {status_filepath.name}")

        except json.JSONDecodeError as e:
            print(f"Orchestrator: JSON error processing trigger file {trigger_file.name} or agent output: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Orchestrator: Error processing trigger file {trigger_file.name}: {e}", file=sys.stderr)

if __name__ == "__main__":
    # This script is intended to be run in a loop or as a background service
    # For this OpenClaw context, I will run it in the background as a process
    print("Orchestrator: Starting in continuous mode. Watching for trigger files...")
    while True:
        orchestrate_planner_agent()
        time.sleep(5) # Check every 5 seconds
