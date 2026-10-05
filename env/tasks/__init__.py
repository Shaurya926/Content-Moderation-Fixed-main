from .easy_task import EASY_SAMPLES
from .medium_task import MEDIUM_SAMPLES
from .hard_task import HARD_SAMPLES

TASK_REGISTRY = {
    "spam_detection": EASY_SAMPLES,
    "offensive_content": MEDIUM_SAMPLES,
    "context_moderation": HARD_SAMPLES,
}