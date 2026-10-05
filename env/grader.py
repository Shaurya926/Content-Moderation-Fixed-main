"""
grader.py — Deterministic Grader for Content Moderation Environment.

CRITICAL: All scores are STRICTLY between 0 and 1 — open interval (0, 1).
No score can ever be exactly 0.0 or exactly 1.0.
Range is always (0.01, 0.99).
"""

from dataclasses import dataclass

ACTION_NAMES = {0: "allow", 1: "warn", 2: "remove", 3: "ban"}

# Hard bounds — scores can NEVER touch 0.0 or 1.0
SCORE_MIN = 0.01
SCORE_MAX = 0.99

# Severity distance → base score. NO 0.0, NO 1.0 anywhere.
SEVERITY_DISTANCE_SCORE = {
    0: 0.99,  # Exact match        → near-perfect  (NOT 1.0)
    1: 0.60,  # Off by 1 level     → partial credit
    2: 0.20,  # Off by 2 levels    → low credit
    3: 0.05,  # Completely wrong   → minimal        (NOT 0.0)
}

# Per-label penalty rules — no penalty can push score to exactly 0.0
LABEL_RULES = {
    "spam":                   {"under_penalty": 0.00, "over_penalty": 0.45},
    "offensive":              {"under_penalty": 0.00, "over_penalty": 0.35},
    "severe_harassment":      {"under_penalty": 0.00, "over_penalty": 0.25},
    "hate_speech":            {"under_penalty": 0.00, "over_penalty": 0.25},
    "mild_offensive":         {"under_penalty": 0.15, "over_penalty": 0.35},
    "incitement":             {"under_penalty": 0.00, "over_penalty": 0.15},
    "coordinated_harassment": {"under_penalty": 0.00, "over_penalty": 0.15},
    "threat":                 {"under_penalty": 0.00, "over_penalty": 0.15},
    "veiled_threat":          {"under_penalty": 0.00, "over_penalty": 0.25},
    "borderline_hate":        {"under_penalty": 0.10, "over_penalty": 0.45},
    "coded_hate":             {"under_penalty": 0.00, "over_penalty": 0.35},
    "self_harm_signal":       {"under_penalty": 0.10, "over_penalty": 0.45},
    "safe":                   {"under_penalty": 0.45, "over_penalty": 0.00},
    "sarcasm_safe":           {"under_penalty": 0.45, "over_penalty": 0.00},
    "safe_frustration":       {"under_penalty": 0.45, "over_penalty": 0.00},
    "safe_opinion":           {"under_penalty": 0.45, "over_penalty": 0.00},
    "safe_commentary":        {"under_penalty": 0.45, "over_penalty": 0.00},
}


def _clamp(value: float) -> float:
    """Clamp to open interval (0.01, 0.99). NEVER 0.0 or 1.0."""
    return round(max(SCORE_MIN, min(SCORE_MAX, value)), 4)


@dataclass
class GraderResult:
    sample_id: str
    taken_action: int
    expected_action: int
    label: str
    score: float        # strictly in (0.01, 0.99)
    exact_match: bool
    severity_delta: int
    explanation: str


def grade_single(
    sample_id: str,
    taken_action: int,
    expected_action: int,
    label: str,
) -> GraderResult:
    """
    Grade one moderation decision. Score is STRICTLY in (0.01, 0.99).
    Never returns 0.0 or 1.0.
    """
    severity_delta = abs(taken_action - expected_action)
    exact_match = severity_delta == 0

    base_score = SEVERITY_DISTANCE_SCORE.get(severity_delta, SCORE_MIN)

    if exact_match:
        score = _clamp(base_score)  # 0.99 max, never 1.0
        explanation = f"Exact match: {ACTION_NAMES[taken_action]} score={score}"
        return GraderResult(
            sample_id=sample_id,
            taken_action=taken_action,
            expected_action=expected_action,
            label=label,
            score=score,
            exact_match=True,
            severity_delta=0,
            explanation=explanation,
        )

    rules = LABEL_RULES.get(label, {"under_penalty": 0.25, "over_penalty": 0.25})

    if taken_action < expected_action:
        penalty   = rules["under_penalty"]
        direction = "under-blocked (too lenient)"
    else:
        penalty   = rules["over_penalty"]
        direction = "over-blocked (too strict)"

    score = _clamp(base_score - penalty)  # always stays in (0.01, 0.99)

    explanation = (
        f"Mismatch: took={ACTION_NAMES[taken_action]} "
        f"expected={ACTION_NAMES[expected_action]} "
        f"({direction}) base={base_score:.2f} "
        f"penalty={penalty:.2f} score={score}"
    )

    return GraderResult(
        sample_id=sample_id,
        taken_action=taken_action,
        expected_action=expected_action,
        label=label,
        score=score,
        exact_match=False,
        severity_delta=severity_delta,
        explanation=explanation,
    )


def grade_episode(results: list[GraderResult]) -> dict:
    """
    Aggregate results into final episode score.
    Episode score is STRICTLY in (0.01, 0.99). Never 0.0 or 1.0.
    """
    if not results:
        return {"episode_score": 0.05, "breakdown": {}}  # NOT 0.0

    scores        = [r.score for r in results]
    exact_matches = sum(1 for r in results if r.exact_match)
    under_blocks  = sum(1 for r in results if not r.exact_match and r.taken_action < r.expected_action)
    over_blocks   = sum(1 for r in results if not r.exact_match and r.taken_action > r.expected_action)

    raw_mean      = sum(scores) / len(scores)
    episode_score = _clamp(raw_mean)  # strictly (0.01, 0.99)

    return {
        "episode_score": episode_score,
        "total_steps":   len(results),
        "exact_matches": exact_matches,
        "accuracy":      round(exact_matches / len(results), 4),
        "under_blocks":  under_blocks,
        "over_blocks":   over_blocks,
        "mean_score":    episode_score,
        "min_score":     _clamp(min(scores)),
        "max_score":     _clamp(max(scores)),
    }
