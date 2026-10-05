"""
models.py — Typed Pydantic models for Content Moderation Environment.
All models follow OpenEnv spec: Observation, Action, Reward, and API response types.
"""

from typing import Any
from pydantic import BaseModel, Field


# ─────────────────────────────────────────────
# Core Domain Models
# ─────────────────────────────────────────────

class UserHistory(BaseModel):
    """Historical context about the posting user."""
    account_age_days: int = Field(ge=0, description="Days since account creation")
    previous_violations: int = Field(ge=0, description="Number of past violations")
    post_count: int = Field(ge=0, description="Total posts made")


class PostContext(BaseModel):
    """Contextual metadata about where/how the post was made."""
    platform: str = Field(description="Platform type: social_media, forum, chat")
    post_type: str = Field(description="Type: post, comment, dm, story")
    reported: bool = Field(description="Whether the post was reported by users")


class ExtractedFeatures(BaseModel):
    """Pre-computed NLP features for the agent (avoids raw NLP complexity)."""
    has_spam_keywords: bool = Field(description="Contains spam trigger words")
    has_offensive_words: bool = Field(description="Contains offensive language")
    toxicity_score: float = Field(ge=0.0, le=1.0, description="0=clean, 1=very toxic")
    sentiment_score: float = Field(ge=-1.0, le=1.0, description="-1=negative, +1=positive")
    has_urls: bool = Field(description="Contains links")
    caps_ratio: float = Field(ge=0.0, le=1.0, description="Ratio of uppercase letters")


# ─────────────────────────────────────────────
# OpenEnv Core Models
# ─────────────────────────────────────────────

class Observation(BaseModel):
    """What the agent observes at each step."""
    post_text: str = Field(description="The social media post content")
    user_history: UserHistory = Field(description="Posting user's history")
    context: PostContext = Field(description="Post context metadata")
    extracted_features: ExtractedFeatures = Field(description="Pre-computed NLP features")
    step: int = Field(ge=0, description="Current step number")
    task_id: str = Field(description="Active task identifier")
    label: str = Field(description="Ground truth label (for logging/debug)")
    total_steps: int = Field(description="Total steps in episode")


class Action(BaseModel):
    """Agent's moderation decision."""
    action: int = Field(
        ge=0, le=3,
        description="0=allow, 1=warn, 2=remove, 3=ban"
    )

    @property
    def name(self) -> str:
        return {0: "allow", 1: "warn", 2: "remove", 3: "ban"}[self.action]


class RewardBreakdown(BaseModel):
    """Detailed breakdown of reward components."""
    base_reward: float
    streak_bonus: float
    repetition_penalty: float
    severity_mismatch_penalty: float
    total: float


class Reward(BaseModel):
    """Reward signal with full breakdown for transparency."""
    value: float = Field(description="Total reward for this step")
    breakdown: RewardBreakdown
    correct: bool = Field(description="Whether the action was correct")
    expected_action: int
    taken_action: int


# ─────────────────────────────────────────────
# API Response Models
# ─────────────────────────────────────────────

class StepResponse(BaseModel):
    """Response from POST /step."""
    observation: Observation
    reward: float
    done: bool
    info: dict[str, Any]


class ResetResponse(BaseModel):
    """Response from POST /reset."""
    observation: Observation
    task_id: str
    message: str


class StateResponse(BaseModel):
    """Response from GET /state — full environment state."""
    task_id: str
    step: int
    total_steps: int
    done: bool
    cumulative_reward: float
    action_history: list[int]
    reward_history: list[float]
    correct_count: int
    accuracy: float
    current_observation: Observation | None


class ResetRequest(BaseModel):
    """Optional body for POST /reset."""
    task_id: str = "spam_detection"
