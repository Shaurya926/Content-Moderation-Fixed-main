"""
environment.py — Content Moderation RL Environment.

Implements the full OpenEnv interface:
  reset()  → initial observation
  step()   → observation, reward, done, info
  state()  → current full state
"""

from copy import deepcopy
from typing import Any

from .models import (
    Action,
    ExtractedFeatures,
    Observation,
    PostContext,
    Reward,
    RewardBreakdown,
    StateResponse,
    UserHistory,
)
from .tasks import TASK_REGISTRY
from .grader import grade_single, grade_episode, GraderResult

ACTION_NAMES = {0: "allow", 1: "warn", 2: "remove", 3: "ban"}

# ─────────────────────────────────────────────
# Reward Configuration
# ─────────────────────────────────────────────

BASE_REWARDS = {
    "exact": 1.0,          # Correct action
    "wrong": -1.0,         # Clearly wrong action
    "under_block_hard": -2.0,  # Missing genuine harm on hard task
    "near_miss": 0.4,      # Off by one severity level
}

STREAK_BONUS = 0.2          # Bonus for 3+ consecutive correct
REPEAT_MISTAKE_PENALTY = -0.2  # Repeated same wrong action
SUSPICIOUS_ABUSE_PENALTY = -0.1  # If agent always picks same action


class ContentModerationEnv:
    """
    Content Moderation Environment.

    An AI agent observes social media posts and must decide:
      0 = allow, 1 = warn, 2 = remove, 3 = ban

    The environment tracks history and provides shaped rewards
    to guide learning across a full trajectory.
    """

    VALID_TASKS = list(TASK_REGISTRY.keys())

    def __init__(self) -> None:
        self._task_id: str = "spam_detection"
        self._samples: list[dict] = []
        self._step: int = 0
        self._done: bool = True
        self._cumulative_reward: float = 0.0
        self._action_history: list[int] = []
        self._reward_history: list[float] = []
        self._grader_results: list[GraderResult] = []
        self._correct_streak: int = 0
        self._last_wrong_action: int | None = None
        self._current_sample: dict | None = None

    # ─────────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────────

    def reset(self, task_id: str = "spam_detection") -> Observation:
        """Initialize environment for a given task. Returns first observation."""
        if task_id not in TASK_REGISTRY:
            raise ValueError(
                f"Unknown task '{task_id}'. Valid: {self.VALID_TASKS}"
            )

        self._task_id = task_id
        self._samples = deepcopy(TASK_REGISTRY[task_id])
        self._step = 0
        self._done = False
        self._cumulative_reward = 0.0
        self._action_history = []
        self._reward_history = []
        self._grader_results = []
        self._correct_streak = 0
        self._last_wrong_action = None

        self._current_sample = self._samples[self._step]
        return self._build_observation()

    def step(self, action: Action) -> tuple[Observation, float, bool, dict[str, Any]]:
        """
        Process one moderation decision.

        Returns:
            observation: next post to moderate (or terminal state)
            reward: shaped reward for this action
            done: episode complete flag
            info: debugging information
        """
        if self._done:
            raise RuntimeError("Episode is done. Call reset() first.")

        sample = self._current_sample
        expected_action = sample["expected_action"]
        taken_action = action.action

        # Grade this step
        grade = grade_single(
            sample_id=sample["id"],
            taken_action=taken_action,
            expected_action=expected_action,
            label=sample["label"],
        )
        self._grader_results.append(grade)

        # Compute shaped reward
        reward_obj = self._compute_reward(taken_action, expected_action, sample)
        reward = reward_obj.value

        # Update tracking
        self._action_history.append(taken_action)
        self._reward_history.append(reward)
        self._cumulative_reward += reward

        if grade.exact_match:
            self._correct_streak += 1
            self._last_wrong_action = None
        else:
            self._correct_streak = 0
            self._last_wrong_action = taken_action

        # Advance step
        self._step += 1
        self._done = self._step >= len(self._samples)

        if not self._done:
            self._current_sample = self._samples[self._step]
            obs = self._build_observation()
        else:
            obs = self._build_terminal_observation()

        info = {
            "sample_id": sample["id"],
            "expected_action": expected_action,
            "expected_action_name": ACTION_NAMES[expected_action],
            "taken_action_name": ACTION_NAMES[taken_action],
            "label": sample["label"],
            "correct": grade.exact_match,
            "grader_score": grade.score,
            "grader_explanation": grade.explanation,
            "reward_breakdown": reward_obj.breakdown.model_dump(),
            "streak": self._correct_streak,
            "cumulative_reward": self._cumulative_reward,
        }

        return obs, reward, self._done, info

    def state(self) -> StateResponse:
        """Return the complete current state of the environment."""
        total = len(self._samples)
        correct = sum(1 for g in self._grader_results if g.exact_match)
        accuracy = correct / len(self._grader_results) if self._grader_results else 0.0

        return StateResponse(
            task_id=self._task_id,
            step=self._step,
            total_steps=total,
            done=self._done,
            cumulative_reward=round(self._cumulative_reward, 4),
            action_history=self._action_history,
            reward_history=[round(r, 4) for r in self._reward_history],
            correct_count=correct,
            accuracy=round(accuracy, 4),
            current_observation=(
                self._build_observation() if not self._done else None
            ),
        )

    def get_episode_score(self) -> dict:
        """Return aggregated grader score for the full episode (0.0–1.0)."""
        return grade_episode(self._grader_results)

    # ─────────────────────────────────────────────
    # Internal Helpers
    # ─────────────────────────────────────────────

    def _build_observation(self) -> Observation:
        s = self._current_sample
        return Observation(
            post_text=s["post_text"],
            user_history=UserHistory(**s["user_history"]),
            context=PostContext(**s["context"]),
            extracted_features=ExtractedFeatures(**s["extracted_features"]),
            step=self._step,
            task_id=self._task_id,
            label=s["label"],
            total_steps=len(self._samples),
        )

    def _build_terminal_observation(self) -> Observation:
        """Dummy observation returned when episode ends."""
        last = self._samples[-1]
        return Observation(
            post_text="[EPISODE COMPLETE]",
            user_history=UserHistory(**last["user_history"]),
            context=PostContext(**last["context"]),
            extracted_features=ExtractedFeatures(**last["extracted_features"]),
            step=self._step,
            task_id=self._task_id,
            label="terminal",
            total_steps=len(self._samples),
        )

    def _compute_reward(
        self,
        taken: int,
        expected: int,
        sample: dict,
    ) -> Reward:
        """
        Sophisticated reward shaping.

        Components:
          1. Base reward: correctness + severity distance
          2. Streak bonus: consistent correct decisions
          3. Repetition penalty: stuck on wrong action
          4. Severity mismatch: extra penalty for catastrophic misses
        """
        severity_delta = abs(taken - expected)
        exact = severity_delta == 0
        label = sample["label"]

        # 1. Base reward
        if exact:
            base_reward = BASE_REWARDS["exact"]
        elif severity_delta == 1:
            base_reward = BASE_REWARDS["near_miss"]
        else:
            base_reward = BASE_REWARDS["wrong"]

        # Hard task under-blocking penalty (missing real harm)
        severity_mismatch_penalty = 0.0
        if not exact and taken < expected:
            # Under-blocked: agent too lenient
            if label in ("threat", "incitement", "coordinated_harassment", "veiled_threat"):
                severity_mismatch_penalty = -1.0  # Heavy penalty for missing serious harm
            elif label in ("hate_speech", "offensive", "severe_harassment"):
                severity_mismatch_penalty = -0.5

        # Over-blocking safe content
        if not exact and taken > expected and "safe" in label:
            severity_mismatch_penalty = -0.5

        # 2. Streak bonus (3+ consecutive correct)
        streak_bonus = STREAK_BONUS if (exact and self._correct_streak >= 2) else 0.0

        # 3. Repetition penalty (same wrong action repeated)
        repetition_penalty = 0.0
        if (
            not exact
            and self._last_wrong_action is not None
            and taken == self._last_wrong_action
        ):
            repetition_penalty = REPEAT_MISTAKE_PENALTY

        # 4. Action abuse penalty (agent always picks same action)
        abuse_penalty = 0.0
        if len(self._action_history) >= 4:
            last_4 = self._action_history[-4:]
            if len(set(last_4)) == 1 and not exact:
                abuse_penalty = SUSPICIOUS_ABUSE_PENALTY

        total = base_reward + streak_bonus + repetition_penalty + severity_mismatch_penalty + abuse_penalty
        total = round(max(-2.0, min(1.2, total)), 4)

        breakdown = RewardBreakdown(
            base_reward=round(base_reward, 4),
            streak_bonus=round(streak_bonus, 4),
            repetition_penalty=round(repetition_penalty, 4),
            severity_mismatch_penalty=round(severity_mismatch_penalty, 4),
            total=total,
        )

        return Reward(
            value=total,
            breakdown=breakdown,
            correct=exact,
            expected_action=expected,
            taken_action=taken,
        )
