# LevelUp Application: Features Plan

## 1. Overall Application Goal

To provide a personalized, adaptive 90-day upskilling and revision program for the user (Deepak Naik), leveraging an army of AI agents to plan, execute, reflect, and adapt the learning journey. The application will be a production-ready system with a Python FastAPI backend and a React frontend.

## 2. Core Agents & Their Responsibilities

As defined in the core idea, these agents will operate in a closed-loop learning engine:

*   **Planner Agent:**
    *   **Role:** Creates the initial 7-30 day structured learning roadmap based on user goals, time commitment, and skill level.
    *   **Input (from Orchestrator/API):** `UserGoal` (string), `TimePerDay` (minutes, int), `SkillLevel` (enum: "beginner", "intermediate", "advanced").
    *   **Output (to Orchestrator/API):** Structured JSON representing the `plan.json` format, including daily themes and actionable tasks (learn, apply, reflect).

*   **Executor Coach Agent:**
    *   **Role:** Drives daily action, guiding the user to complete today's plan by presenting one task at a time, providing nudges, and acknowledging completion.
    *   **Input (from Orchestrator/API):** Today's tasks (from `plan.json`), User history (completed/missed tasks from `history.json`).
    *   **Output (to Orchestrator/User):** `current_task` (JSON with title, instruction, estimated_time), `nudge` (string).

*   **Reflector Agent:**
    *   **Role:** Extracts key insights and learning signals from user reflections, focusing on understanding, unclear areas, and patterns.
    *   **Input (from Orchestrator/API):** Completed tasks (from `history.json`), `UserReflections` (text).
    *   **Output (to Orchestrator/API):** `insights` (list of strings), `weak_areas` (list of strings), `confidence_level` (enum: "low", "medium", "high") (JSON, stored in `LevelUp/data/insights.json`).

*   **Adaptation Engine Agent:**
    *   **Role:** Adjusts the next day's plan based on reflection insights and missed tasks, ensuring learning feels progressive.
    *   **Input (from Orchestrator/API):** Current plan (from `plan.json`), Reflection insights (from `insights.json`), Missed tasks (from `history.json`).
    *   **Output (to Orchestrator/API):** `adjusted_day_plan` (JSON, updates `LevelUp/data/plan.json`), `reason` (string explaining the adjustment).

*   **Content Fetcher Agent (Optional - Phase 3+):**
    *   **Role:** Provides relevant learning resources (YouTube video, high-quality article) for a given topic.
    *   **Input (from Orchestrator/API):** `Topic` (string).
    *   **Output (to Orchestrator/API):** `video` (JSON with title, url), `article` (JSON with title, url).

## 3. Backend (FastAPI) Feature Plan

The FastAPI backend will serve as the API layer, orchestrating the agents, managing data persistence, and serving the frontend.

*   **Core Responsibilities:**
    *   Provide RESTful API endpoints for the frontend.
    *   Load, save, and manage `plan.json`, `history.json`, `insights.json`.
    *   Spawn and manage OpenClaw sub-agent sessions for Planner, Reflector, and Adaptation Engine.
    *   Handle asynchronous communication with sub-agents and process their structured JSON outputs.
    *   Implement data validation and error handling.
    *   CORS configuration for frontend integration.

*   **API Endpoints (Conceptual):**

    *   `POST /api/v1/plan/generate`
        *   **Description:** Initiates the learning plan creation.
        *   **Input (Request Body - JSON):**
            ```json
            {
              "user_goal": "string",
              "time_per_day_minutes": 60,
              "skill_level": "intermediate"
            }
            ```
        *   **Output (Response Body - JSON):**
            ```json
            {
              "message": "Learning plan generation initiated.",
              "plan_id": "uuid_of_plan"
            }
            ```
        *   **Process:** Spawns Planner Agent, waits for result, saves to `plan.json`.

    *   `GET /api/v1/plan/current`
        *   **Description:** Retrieves the current day's learning plan and tasks.
        *   **Output (Response Body - JSON):**
            ```json
            {
              "current_day": 1,
              "theme": "Advanced JavaScript & ESNext Features",
              "tasks": [
                {"type": "learn", "title": "...", "duration": "...", "status": "pending"},
                {"type": "apply", "title": "...", "duration": "...", "status": "pending"},
                {"type": "reflect", "question": "...", "status": "pending"}
              ],
              "user_history_summary": { ... } // High-level summary from history.json
            }
            ```
        *   **Process:** Reads `plan.json` and `history.json` to determine and return today's tasks and context.

    *   `POST /api/v1/task/complete`
        *   **Description:** Marks a specific task as completed by the user.
        *   **Input (Request Body - JSON):**
            ```json
            {
              "day": 1,
              "task_index": 0,
              "completion_details": "optional_text_from_user"
            }
            ```
        *   **Output (Response Body - JSON):**
            ```json
            {
              "message": "Task marked as complete.",
              "history_updated": true
            }
            ```
        *   **Process:** Updates `history.json`.

    *   `POST /api/v1/reflection/submit`
        *   **Description:** Submits the user's reflection for the day.
        *   **Input (Request Body - JSON):**
            ```json
            {
              "day": 1,
              "reflection_text": "string"
            }
            ```
        *   **Output (Response Body - JSON):**
            ```json
            {
              "message": "Reflection submitted. Analyzing insights...",
              "insight_analysis_initiated": true
            }
            ```
        *   **Process:** Saves reflection, spawns Reflector Agent, waits for result, saves to `insights.json`.

    *   `GET /api/v1/insights/latest`
        *   **Description:** Retrieves the latest learning insights from the Reflector Agent.
        *   **Output (Response Body - JSON):**
            ```json
            {
              "insights": ["...", "..."],
              "weak_areas": ["...", "..."],
              "confidence_level": "medium",
              "last_updated": "timestamp"
            }
            ```
        *   **Process:** Reads `insights.json`.

    *   `POST /api/v1/plan/adapt`
        *   **Description:** Triggers the Adaptation Engine to adjust the plan.
        *   **Input (Request Body - JSON):** (Likely an internal trigger, or a simple `{"confirm": true}` from frontend if manual override is desired)
        *   **Output (Response Body - JSON):**
            ```json
            {
              "message": "Plan adaptation initiated.",
              "new_plan_version": "uuid_of_new_plan"
            }
            ```
        *   **Process:** Spawns Adaptation Engine, waits for result, updates `plan.json`.

    *   `GET /api/v1/content/fetch` (Optional)
        *   **Description:** Fetches learning resources for a given topic.
        *   **Input (Query Parameter):** `topic=string`
        *   **Output (Response Body - JSON):**
            ```json
            {
              "topic": "string",
              "video": {"title": "string", "url": "string"},
              "article": {"title": "string", "url": "string"}
            }
            ```
        *   **Process:** Spawns Content Fetcher Agent, waits for result.

*   **Data Models (Pydantic):**
    *   `PlanGenerateRequest`, `TaskCompletionRequest`, `ReflectionSubmitRequest`, etc.
    *   `CurrentPlanResponse`, `LatestInsightsResponse`, `ContentFetchResponse`, etc.

*   **File I/O Module:** A dedicated Python module (e.g., `LevelUp/backend/app/crud.py` or `LevelUp/backend/app/data_manager.py`) to handle loading and saving the JSON files in `LevelUp/data/`.

## 4. Frontend (React) Feature Plan

The React frontend will provide the user interface for interacting with the learning program.

*   **Core Responsibilities:**
    *   Display current learning tasks and themes.
    *   Allow users to mark tasks complete and submit reflections.
    *   Present learning insights and adapted plans.
    *   Handle user input for goal setting.
    *   Communicate with the FastAPI backend via API calls.

*   **Main User Flows/Pages:**

    *   **`Onboarding / Goal Setting Page` (`/onboarding`):**
        *   **Description:** Captures initial user input for `UserGoal`, `TimePerDay`, `SkillLevel`.
        *   **Interaction:** Form with input fields, submit button.
        *   **API Call:** `POST /api/v1/plan/generate`

    *   **`Daily Dashboard Page` (`/dashboard`):**
        *   **Description:** The primary page for daily interaction. Displays the current day's theme, a list of tasks, and an interface to interact with tasks.
        *   **Interaction:**
            *   Displays current day number and theme.
            *   Lists tasks for the day.
            *   "Mark Complete" button for `apply` / `learn` tasks.
            *   Text area for `reflect` task, with a "Submit Reflection" button.
        *   **API Calls:**
            *   `GET /api/v1/plan/current` (on load)
            *   `POST /api/v1/task/complete`
            *   `POST /api/v1/reflection/submit`

    *   **`Insights / Progress Page` (`/insights`):** (Future Phase)
        *   **Description:** Displays the insights gathered by the Reflector Agent and overall learning progress.
        *   **Interaction:** Visualizations (charts for progress, skill growth), textual display of `insights` and `weak_areas`.
        *   **API Call:** `GET /api/v1/insights/latest`

*   **Key React Components (Conceptual):**

    *   `App.js`: Main application layout, routing.
    *   `OnboardingForm.js`: Component for goal setting.
    *   `DailyTaskView.js`: Orchestrates display of tasks, handles task completion/reflection submission.
    *   `TaskCard.js`: Individual task display component.
    *   `ReflectionInput.js`: Component for user reflection.
    *   `LoadingSpinner.js`: For API call states.

*   **State Management:**
    *   Use React's `useState` and `useEffect` for local component state.
    *   Consider `Context API` or a small library like `Zustand` or `Jotai` for global application state (e.g., user profile, current plan data).

*   **API Integration:**
    *   Utilize `fetch` API or `axios` for HTTP requests to the FastAPI backend.
    *   Handle loading, error states, and data rendering.

## 5. Data Persistence

*   **Current State:** JSON files (`plan.json`, `history.json`, `insights.json`) stored in `LevelUp/data/`. These files will be loaded and saved by the FastAPI backend.
*   **Future Consideration:** For a more robust production environment, moving to a lightweight database (e.g., SQLite for simplicity, PostgreSQL for scalability) would be beneficial. This would involve updating the backend's data management module.

## 6. Next Steps - Implementation Sequence

**Phase 1: Foundation (Completed)**
- [x] 1.  **Backend - Data Manager:** Implement a module in FastAPI to safely read/write `plan.json`, `history.json`, `insights.json`.
- [x] 2.  **Backend - Planner API:** Implement the `POST /api/v1/plan/generate` endpoint, including spawning the Planner Agent and saving its output.
- [x] 3.  **Frontend - Onboarding Page:** Build the `/onboarding` page to capture user input and call the `POST /api/v1/plan/generate` API.
- [x] 4.  **Backend - Current Plan API:** Implement `GET /api/v1/plan/current`.

**Phase 2: Daily Execution (In Progress)**
- [ ] 5.  **Frontend - Daily Dashboard:** Build the `/dashboard` page to display the current day's learning theme and tasks, calling `GET /api/v1/plan/current`.
- [ ] 6.  **Backend - Task Completion API:** Implement `POST /api/v1/task/complete` to update `history.json`.
- [ ] 7.  **Backend - Reflection API:** Implement `POST /api/v1/reflection/submit` to store user reflections.
- [ ] 8.  **Frontend - Task Interaction:** Add UI elements on the dashboard for task completion and submitting daily reflections.

**Phase 3: Reflection & Adaptation (Upcoming)**
- [ ] 9.  **Backend - Reflector Agent Integration:** Spawn Reflector Agent after reflection submission to generate `insights.json`.
- [ ] 10. **Backend - Adaptation Engine Integration:** Integrate the Adaptation Engine to dynamically modify the plan based on missed tasks and insights.
- [ ] 11. **Frontend - Insights Display:** Build an insights view to visualize `insights` and `weak_areas`.

**Phase 4: Enhancements**
- [ ] 12. **Content Fetcher:** Implement the optional Content Fetcher agent and its corresponding API/UI.

---

This plan outlines the architecture, features, and an implementation sequence for our LevelUp application. Detailed status and breakdown can be found in `task.md`.