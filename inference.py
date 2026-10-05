"""
inference.py — Baseline Inference for Content Moderation Environment.

MANDATORY STDOUT FORMAT (exact — Output Parsing checks this):
    [START] task=<task_name> env=<benchmark> model=<model_name>
    [STEP]  step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
    [END]   success=<true|false> steps=<n> score=<0.000> rewards=<r1,r2,...,rn>

Environment variables (mandatory):
    API_BASE_URL   LLM endpoint
    MODEL_NAME     Model identifier
    HF_TOKEN       Hugging Face / API key
"""

import os
import sys
import json
import time
import subprocess

# ── Env vars ─────────────────────────────────────────────────────────────────
API_BASE_URL  = os.environ.get("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME    = os.environ.get("MODEL_NAME",   "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN      = os.environ.get("HF_TOKEN", "") or os.environ.get("OPENAI_API_KEY", "dummy-key")
ENV_BASE_URL  = os.environ.get("ENV_BASE_URL", "http://localhost:7860")

BENCHMARK     = "content-moderation"
TASKS         = ["spam_detection", "offensive_content", "context_moderation"]
ACTION_NAMES  = {0: "allow", 1: "warn", 2: "remove", 3: "ban"}
MAX_STEPS     = 15
MAX_TOKENS    = 80
TEMPERATURE   = 0.0
SUCCESS_THRESHOLD = 0.5   # score >= this → success=true

SYSTEM_PROMPT = (
    "You are a social media content moderation AI.\n"
    "Choose exactly one action:\n"
    "  0 = allow  (safe, harmless content)\n"
    "  1 = warn   (mildly problematic — warn user)\n"
    "  2 = remove (clearly harmful — delete post)\n"
    "  3 = ban    (severe or repeat offender — ban user)\n"
    'Reply ONLY with valid JSON: {"action": <0|1|2|3>, "reason": "<one sentence>"}'
)

# ── Safe imports ──────────────────────────────────────────────────────────────
try:
    import requests as _req
except ImportError:
    sys.exit("[ERROR] pip install requests")

try:
    from openai import OpenAI
except ImportError:
    sys.exit("[ERROR] pip install openai")

# ── Exact log helpers (Output Parsing reads these) ────────────────────────────

def log_start(task: str) -> None:
    print(f"[START] task={task} env={BENCHMARK} model={MODEL_NAME}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error) -> None:
    error_val = error if error else "null"
    print(
        f"[STEP] step={step} action={action} "
        f"reward={reward:.2f} done={str(done).lower()} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: list) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} "
        f"score={score:.3f} rewards={rewards_str}",
        flush=True,
    )


# ── Server management ─────────────────────────────────────────────────────────

_server_proc = None


def _is_up() -> bool:
    try:
        return _req.get(f"{ENV_BASE_URL}/health", timeout=4).status_code == 200
    except Exception:
        return False


def _start_server() -> bool:
    global _server_proc
    root = os.path.dirname(os.path.abspath(__file__))
    app  = os.path.join(root, "app.py")
    if not os.path.exists(app):
        return False
    try:
        _server_proc = subprocess.Popen(
            [sys.executable, app], cwd=root,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    except Exception:
        return False
    for i in range(20):
        time.sleep(1)
        if _is_up():
            return True
    return False


def _stop_server():
    global _server_proc
    if _server_proc:
        try:
            _server_proc.terminate()
            _server_proc.wait(timeout=5)
        except Exception:
            pass
        _server_proc = None


# ── Env API helpers ───────────────────────────────────────────────────────────

def call_env(endpoint, method="GET", body=None):
    try:
        url = f"{ENV_BASE_URL}{endpoint}"
        r = _req.post(url, json=body or {}, timeout=15) if method == "POST" \
            else _req.get(url, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[DEBUG] env call failed {endpoint}: {e}", flush=True)
        return None


# ── LLM helpers ───────────────────────────────────────────────────────────────

def build_prompt(obs: dict) -> str:
    try:
        f = obs.get("extracted_features", {})
        u = obs.get("user_history", {})
        c = obs.get("context", {})
        t = obs.get("post_text", "")[:300]
        return (
            f'POST: "{t}"\n'
            f"USER: age={u.get('account_age_days')}d "
            f"violations={u.get('previous_violations')} "
            f"posts={u.get('post_count')}\n"
            f"CTX: platform={c.get('platform')} "
            f"type={c.get('post_type')} "
            f"reported={c.get('reported')}\n"
            f"FEATURES: toxicity={f.get('toxicity_score')} "
            f"spam={f.get('has_spam_keywords')} "
            f"offensive={f.get('has_offensive_words')} "
            f"sentiment={f.get('sentiment_score')} "
            f"caps={f.get('caps_ratio')}\n"
            "Reply with JSON only."
        )
    except Exception:
        return f"POST: \"{obs.get('post_text','')[:200]}\"\nReply JSON only."


def get_action(client: "OpenAI", obs: dict) -> tuple:
    """Return (action_int, action_str). Never raises."""
    try:
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": build_prompt(obs)},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        raw = (resp.choices[0].message.content or "").strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(raw)
        a = max(0, min(3, int(parsed.get("action", 0))))
        return a, ACTION_NAMES[a]
    except json.JSONDecodeError:
        try:
            raw2 = resp.choices[0].message.content or ""
            for ch in raw2:
                if ch in "0123":
                    return int(ch), ACTION_NAMES[int(ch)]
        except Exception:
            pass
        return 0, "allow"
    except Exception:
        return 0, "allow"


# ── Task runner ───────────────────────────────────────────────────────────────

def run_task(client: "OpenAI", task_id: str) -> dict:
    """
    Run one full episode and emit exact [START]/[STEP]/[END] lines.
    Returns summary dict.
    """
    log_start(task=task_id)

    data = call_env("/reset", "POST", {"task_id": task_id})
    if data is None:
        # Can't reset — emit minimal valid output
        log_end(success=False, steps=0, score=0.05, rewards=[])
        return {"task_id": task_id, "episode_score": 0.05, "accuracy": 0.0}

    obs         = data.get("observation", {})
    total_steps = obs.get("total_steps", MAX_STEPS)
    done        = False
    rewards     = []
    steps_done  = 0
    correct     = 0

    for step_num in range(1, total_steps + 1):
        if done:
            break

        action_int, action_str = get_action(client, obs)

        step_data = call_env("/step", "POST", {"action": action_int})
        if step_data is None:
            reward, done, info = 0.0, False, {}
        else:
            reward = float(step_data.get("reward", 0.0))
            done   = bool(step_data.get("done",   False))
            info   = step_data.get("info",   {})
            obs    = step_data.get("observation", obs)

        error_msg = None  # our env doesn't use last_action_error

        # ── Exact [STEP] format ───────────────────────────────────────────────
        log_step(step=step_num, action=action_str, reward=reward,
                 done=done, error=error_msg)

        rewards.append(reward)
        steps_done += 1
        if info.get("correct"):
            correct += 1

    # Get grader score from env (strictly 0.01–0.99 after our fix)
    sc_data = call_env("/score") or {}
    episode_score = sc_data.get("episode_score", correct / max(steps_done, 1))

    # Clamp to (0.001, 0.999) — validator requires strictly between 0 and 1
    episode_score = round(max(0.001, min(0.999, float(episode_score))), 4)

    success = episode_score >= SUCCESS_THRESHOLD

    # ── Exact [END] format ────────────────────────────────────────────────────
    log_end(success=success, steps=steps_done,
            score=episode_score, rewards=rewards)

    return {
        "task_id":       task_id,
        "episode_score": episode_score,
        "accuracy":      round(correct / max(steps_done, 1), 4),
        "steps":         steps_done,
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    # Mandatory: all LLM calls use OpenAI client
    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

    # Ensure server is running
    if not _is_up():
        print("[INFO] Starting environment server...", flush=True)
        if not _start_server():
            print("[WARN] Could not start server — emitting fallback output.", flush=True)
            for t in TASKS:
                log_start(task=t)
                log_end(success=False, steps=0, score=0.05, rewards=[])
            return

    results = []
    for task_id in TASKS:
        try:
            r = run_task(client, task_id)
        except Exception as e:
            print(f"[DEBUG] task {task_id} error: {e}", flush=True)
            log_start(task=task_id)
            log_end(success=False, steps=0, score=0.05, rewards=[])
            r = {"task_id": task_id, "episode_score": 0.05, "accuracy": 0.0}
        results.append(r)

    # Summary (goes to stdout after all [END] lines)
    scores = [r["episode_score"] for r in results]
    avg    = round(sum(scores) / len(scores), 4) if scores else 0.05
    print(f"\n[SUMMARY] avg_score={avg:.4f}", flush=True)

    # Save JSON results
    try:
        out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "baseline_results.json")
        with open(out, "w") as fh:
            json.dump({"model": MODEL_NAME, "results": results, "avg_score": avg}, fh, indent=2)
    except Exception:
        pass


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted.", flush=True)
    except SystemExit:
        raise
    except Exception as e:
        print(f"[FATAL] {e}", flush=True)
        import traceback; traceback.print_exc()
        sys.exit(1)
    finally:
        _stop_server()
