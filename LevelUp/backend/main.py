from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import asyncio
import json
import os

from app.data_manager import load_json_data, save_json_data, find_latest_plan_file

# --- Agent Configuration ---
# In a real setup, these would be managed securely (e.g., environment variables)
PLANNER_AGENT_ID = "LevelUp-Planner-Agent" # Unique label for our Planner Agent

# --- Pydantic Models ---
class PlanGenerateRequest(BaseModel):
    user_goal: str = Field(..., min_length=1, description="The user's overall learning goal.")
    time_per_day_minutes: int = Field(..., gt=0, description="Minutes dedicated to learning per day.")
    skill_level: str = Field(..., pattern="^(beginner|intermediate|advanced)$", description="User's current skill level.")

class PlanGenerateResponse(BaseModel):
    message: str
    plan_id: str | None = None # plan_id will be the request_id until the plan is fully generated

# --- FastAPI App Setup ---
app = FastAPI()

origins = [
    "http://localhost:3000",  # React app default port
    "http://localhost:8000",  # FastAPI default port (if serving static files later or for testing)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Hello from FastAPI backend!"}

# Example endpoint to demonstrate data loading
@app.get("/data/plan")
async def get_plan():
    # In a real app, load this from LevelUp/data/plan.json
    return {"plan": "Your 90-day learning plan goes here."}

@app.post("/api/v1/plan/generate", response_model=PlanGenerateResponse)
async def generate_learning_plan(request: PlanGenerateRequest):
    try:
        # Generate a unique request ID for tracking
        request_id = "plan-req-" + os.urandom(4).hex()
        trigger_filepath_name = f"planner_trigger_{request_id}.json"

        # Save the plan generation request to a trigger file
        save_json_data(trigger_filepath_name, request.model_dump())
        
        # Return an immediate response, the actual plan generation will happen asynchronously
        return PlanGenerateResponse(message="Learning plan generation initiated. Please wait for completion.", plan_id=request_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate plan generation: {str(e)}")

class TaskSchema(BaseModel):
    type: str
    title: str
    duration: str
    status: str = "pending" # Default status

class DayPlanSchema(BaseModel):
    theme: str
    tasks: list[TaskSchema]

class CurrentPlanResponse(BaseModel):
    current_day: int
    theme: str
    tasks: list[TaskSchema]
    user_history_summary: dict = Field(default_factory=dict)

# Existing endpoints...

# Endpoint to get current day's plan
@app.get("/api/v1/plan/current", response_model=CurrentPlanResponse)
async def get_current_learning_plan():
    try:
        # Load the overall plan
        plan = {}
        latest_plan_filename = find_latest_plan_file()
        if latest_plan_filename:
            plan = load_json_data(latest_plan_filename)
        
        if not plan:
            raise HTTPException(status_code=404, detail="Learning plan not found. Please generate one first.")

        # For now, we'll simplify and always show day 1. 
        # In later stages, this will use history.json to determine the actual current day.
        current_day_key = "day_1"
        current_day_data = plan.get(current_day_key)

        if not current_day_data:
            raise HTTPException(status_code=404, detail=f"Plan data for {current_day_key} not found in the latest plan.")

        # Load history (assuming a single active plan for simplicity for now)
        # The history file name now depends on the plan_id from the latest plan
        # We need to extract the plan_id from the latest_plan_filename
        match = re.search(r"plan_(.*?)\.json", latest_plan_filename)
        active_plan_id = match.group(1) if match else ""
        
        history_filepath_name = f"history_{active_plan_id}.json"
        user_history = load_json_data(history_filepath_name)
        
        if not user_history:
            # If history doesn't exist, initialize an empty one for display
            user_history = {"plan_id": active_plan_id, "completed_tasks": [], "missed_tasks": []}

        # Combine plan with history statuses for tasks (simplified for now)
        tasks_with_status = []
        for task_data in current_day_data.get("tasks", []):
            # A more robust implementation would check user_history["completed_tasks"]
            # For now, all tasks are pending in this initial API
            tasks_with_status.append(TaskSchema(**task_data))

        return CurrentPlanResponse(
            current_day=1,
            theme=current_day_data["theme"],
            tasks=tasks_with_status,
            user_history_summary={"completed_count": len(user_history.get("completed_tasks", [])), "total_tasks_today": len(tasks_with_status)}
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve current plan: {str(e)}")

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
