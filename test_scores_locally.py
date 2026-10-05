"""
test_scores_locally.py
======================
Run this BEFORE every submission to catch score range errors.

Usage:
    python test_scores_locally.py

All tests must show OK. If any shows FAIL, do NOT submit.
"""

import sys
import importlib.util
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

# ── Load grader directly (no pydantic needed) ──────────────────────────────
spec = importlib.util.spec_from_file_location("grader", os.path.join(ROOT, "env", "grader.py"))
grader_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grader_mod)

grade_single  = grader_mod.grade_single
grade_episode = grader_mod.grade_episode

# ── Test cases covering ALL edge cases the validator tests ──────────────────
TEST_CASES = [
    # (sample_id, taken_action, expected_action, label)

    # EXACT MATCHES — most likely to produce 1.0 (must be < 1.0)
    ("exact_allow",   0, 0, "safe"),
    ("exact_warn",    1, 1, "mild_offensive"),
    ("exact_remove",  2, 2, "spam"),
    ("exact_ban",     3, 3, "severe_harassment"),
    ("exact_allow2",  0, 0, "sarcasm_safe"),

    # OFF BY 1
    ("off1_under",    1, 2, "spam"),
    ("off1_over",     2, 1, "mild_offensive"),
    ("off1_safe_over",1, 0, "safe"),

    # OFF BY 2
    ("off2_under",    0, 2, "spam"),
    ("off2_over",     3, 1, "mild_offensive"),

    # OFF BY 3 — most likely to produce 0.0 (must be > 0.0)
    ("off3_under",    0, 3, "severe_harassment"),
    ("off3_over",     3, 0, "safe"),

    # HARD TASK LABELS
    ("coded_hate",    0, 2, "coded_hate"),
    ("incitement",    0, 2, "incitement"),
    ("veiled_threat", 0, 2, "veiled_threat"),
    ("self_harm",     0, 1, "self_harm_signal"),
    ("sarcasm_over",  2, 0, "sarcasm_safe"),
    ("safe_over",     3, 0, "safe_frustration"),
    ("commentary",    0, 0, "safe_commentary"),
]

print("=" * 55)
print("  LOCAL SCORE VALIDATOR — run before every submission")
print("=" * 55)
print(f"  Testing {len(TEST_CASES)} individual cases...\n")

results = []
all_ok  = True

for args in TEST_CASES:
    r   = grade_single(*args)
    ok  = 0.0 < r.score < 1.0
    tag = "OK  " if ok else "FAIL"
    if not ok:
        all_ok = False
        print(f"  ❌ [{tag}] score={r.score}  {args[3]} taken={args[1]} exp={args[2]}")
    else:
        print(f"  ✓  [{tag}] score={r.score}  {args[3]} taken={args[1]} exp={args[2]}")
    results.append(r)

# ── Episode score test ──────────────────────────────────────────────────────
print(f"\n  Testing episode aggregation...")

ep   = grade_episode(results)
eps  = ep["episode_score"]
epok = 0.0 < eps < 1.0
if not epok:
    all_ok = False
    print(f"  ❌ [FAIL] episode_score={eps}  ← must be strictly (0, 1)")
else:
    print(f"  ✓  [OK  ] episode_score={eps}")

# ── Edge case: all-perfect episode ─────────────────────────────────────────
perfect = [grade_single(f"p{i}", a, a, "safe") for i, a in enumerate([0,0,0,1,2,3])]
ep_perfect = grade_episode(perfect)
ppok = 0.0 < ep_perfect["episode_score"] < 1.0
if not ppok:
    all_ok = False
    print(f"  ❌ [FAIL] all-perfect episode_score={ep_perfect['episode_score']}")
else:
    print(f"  ✓  [OK  ] all-perfect episode_score={ep_perfect['episode_score']} (not 1.0)")

# ── Edge case: empty episode ────────────────────────────────────────────────
ep_empty = grade_episode([])
emok = 0.0 < ep_empty["episode_score"] < 1.0
if not emok:
    all_ok = False
    print(f"  ❌ [FAIL] empty episode_score={ep_empty['episode_score']}")
else:
    print(f"  ✓  [OK  ] empty episode_score={ep_empty['episode_score']} (not 0.0)")

# ── Final result ────────────────────────────────────────────────────────────
print("\n" + "=" * 55)
if all_ok:
    print("  ✅ ALL TESTS PASSED — safe to submit!")
    print("  Every score is strictly between 0 and 1.")
else:
    print("  ❌ TESTS FAILED — DO NOT SUBMIT!")
    print("  Fix grader.py before submitting.")
print("=" * 55)

sys.exit(0 if all_ok else 1)
