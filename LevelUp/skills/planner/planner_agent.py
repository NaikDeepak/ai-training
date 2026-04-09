import json
import sys
import os

# Assuming Google ADK or a direct Gemini client library would be used here.
# For now, we're mocking the plan generation.

def generate_mock_plan(user_goal: str, time_per_day_minutes: int, skill_level: str):
    # This is a mock implementation. In a real scenario, this would call a Gemini model
    # via Google ADK to generate a truly adaptive plan based on the prompt defined in main.py.

    # We'll generate a simple 7-day plan, slightly tailored
    plan = {}
    for day_num in range(1, 8):
        day_theme = "Core Concepts"
        if day_num == 1:
            day_theme = f"Foundation: {user_goal.split(' ')[0]}"
        elif day_num == 2:
            day_theme = "Advanced JavaScript"
        elif day_num == 3:
            day_theme = "React Deep Dive"
        elif day_num == 4:
            day_theme = "UI Architecture Patterns"
        elif day_num == 5:
            day_theme = "Performance Optimization"
        elif day_num == 6:
            day_theme = "Interview Prep - System Design"
        elif day_num == 7:
            day_theme = "Interview Prep - Coding & Behavioral"

        plan[f"day_{day_num}"] = {
            "theme": day_theme,
            "tasks": [
                {"type": "learn", "title": f"Article on {day_theme}", "duration": f"{int(time_per_day_minutes * 0.4)} mins"},
                {"type": "apply", "title": f"Coding exercise for {day_theme}", "duration": f"{int(time_per_day_minutes * 0.5)} mins"},
                {"type": "reflect", "question": f"What was the most challenging part of {day_theme} today?"}
            ]
        }
    return plan

if __name__ == "__main__":
    # The Planner Agent expects input as a JSON string from stdin or an environment variable
    # For OpenClaw sessions_spawn, the 'task' is passed as the first argument, or stdin.
    # Let's assume it's passed as a single argument for now.
    try:
        input_data_str = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
        input_data = json.loads(input_data_str)

        user_goal = input_data.get("user_goal", "upskilling")
        time_per_day_minutes = input_data.get("time_per_day_minutes", 60)
        skill_level = input_data.get("skill_level", "intermediate")

        generated_plan = generate_mock_plan(user_goal, time_per_day_minutes, skill_level)
        
        # Output the generated plan as a JSON string to stdout
        print(json.dumps(generated_plan, indent=2, ensure_ascii=False))

    except json.JSONDecodeError:
        print("Error: Invalid JSON input to Planner Agent.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error in Planner Agent: {e}", file=sys.stderr)
        sys.exit(1)
