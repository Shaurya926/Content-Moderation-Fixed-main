import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from env.environment import ContentModerationEnv
from env.models import (
    Action,
    ResetRequest,
    ResetResponse,
    StateResponse,
    StepResponse,
)

app = FastAPI(
    title="Content Moderation AI Environment",
    description="RL environment for AI moderation",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

env = ContentModerationEnv()

# ---------- ROUTES ----------
@app.get("/")
def home():
    return {
        "message": "Content Moderation API is running 🚀",
        "docs": "/docs"
    }

@app.post("/reset", response_model=ResetResponse)
def reset(body: ResetRequest | None = None):
    task_id = body.task_id if body and body.task_id else "spam_detection"
    obs = env.reset(task_id=task_id)

    return ResetResponse(
        observation=obs.dict() if hasattr(obs, "dict") else obs,
        task_id=task_id,
        message=f"Episode started. {obs.total_steps} steps total.",
    )

@app.post("/step", response_model=StepResponse)
def step(action: Action):
    obs, reward, done, info = env.step(action)

    return StepResponse(
        observation=obs.dict() if hasattr(obs, "dict") else obs,
        reward=float(reward),
        done=bool(done),
        info=dict(info),
    )

@app.get("/state", response_model=StateResponse)
def state():
    return env.state()

@app.get("/health")
def health():
    return {
        "status": "ok",
        "environment": "content-moderation-env",
        "version": "0.1.0"
    }

@app.get("/tasks")
def list_tasks():
    return {
        "tasks": [
            {"id": "spam_detection", "difficulty": "easy"},
            {"id": "offensive_content", "difficulty": "medium"},
            {"id": "context_moderation", "difficulty": "hard"},
        ]
    }

# ---------- REQUIRED FOR OPENENV ----------
def main():
    uvicorn.run(app, host="0.0.0.0", port=7860)