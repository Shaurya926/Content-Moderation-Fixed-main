"""
medium_task.py — Offensive Content Detection (Medium Difficulty)
15 samples with mixed signals. Agent must calibrate severity correctly:
warn for mild offenses, remove for clear violations, ban for severe/repeat offenders.
"""

MEDIUM_SAMPLES = [
    {
        "id": "med_001",
        "post_text": "People who cut in line deserve to be shamed publicly. Absolute idiots.",
        "user_history": {"account_age_days": 200, "previous_violations": 1, "post_count": 150},
        "context": {"platform": "forum", "post_type": "comment", "reported": True},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": True,
            "toxicity_score": 0.45, "sentiment_score": -0.7,
            "has_urls": False, "caps_ratio": 0.04
        },
        "expected_action": 1,  # warn — mild hostility, first offense
        "label": "mild_offensive",
    },
    {
        "id": "med_002",
        "post_text": "I disagree with the new government policy on education. We need better funding.",
        "user_history": {"account_age_days": 900, "previous_violations": 0, "post_count": 600},
        "context": {"platform": "forum", "post_type": "post", "reported": False},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": False,
            "toxicity_score": 0.08, "sentiment_score": -0.3,
            "has_urls": False, "caps_ratio": 0.02
        },
        "expected_action": 0,  # allow — legitimate political opinion
        "label": "safe",
    },
    {
        "id": "med_003",
        "post_text": "You're so stupid if you believe that. Only brainless fools think like you.",
        "user_history": {"account_age_days": 90, "previous_violations": 3, "post_count": 80},
        "context": {"platform": "social_media", "post_type": "comment", "reported": True},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": True,
            "toxicity_score": 0.72, "sentiment_score": -0.85,
            "has_urls": False, "caps_ratio": 0.06
        },
        "expected_action": 2,  # remove — direct personal attack, repeat offender
        "label": "offensive",
    },
    {
        "id": "med_004",
        "post_text": "This movie was terrible. Waste of 3 hours. The director should quit.",
        "user_history": {"account_age_days": 400, "previous_violations": 0, "post_count": 250},
        "context": {"platform": "social_media", "post_type": "post", "reported": False},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": False,
            "toxicity_score": 0.15, "sentiment_score": -0.6,
            "has_urls": False, "caps_ratio": 0.03
        },
        "expected_action": 0,  # allow — harsh criticism, not personal attack
        "label": "safe",
    },
    {
        "id": "med_005",
        "post_text": "Everyone from that state is corrupt and uneducated. They ruin this country.",
        "user_history": {"account_age_days": 120, "previous_violations": 2, "post_count": 90},
        "context": {"platform": "forum", "post_type": "comment", "reported": True},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": True,
            "toxicity_score": 0.8, "sentiment_score": -0.9,
            "has_urls": False, "caps_ratio": 0.04
        },
        "expected_action": 2,  # remove — regional hate speech
        "label": "hate_speech",
    },
    {
        "id": "med_006",
        "post_text": "Ugh, traffic in Mumbai is the WORST today. 2 hours for 10km 😤",
        "user_history": {"account_age_days": 700, "previous_violations": 0, "post_count": 380},
        "context": {"platform": "social_media", "post_type": "post", "reported": False},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": False,
            "toxicity_score": 0.12, "sentiment_score": -0.5,
            "has_urls": False, "caps_ratio": 0.08
        },
        "expected_action": 0,  # allow — frustration, no violation
        "label": "safe",
    },
    {
        "id": "med_007",
        "post_text": "I hate you so much. You're a worthless piece of garbage. Go delete yourself.",
        "user_history": {"account_age_days": 45, "previous_violations": 8, "post_count": 60},
        "context": {"platform": "social_media", "post_type": "comment", "reported": True},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": True,
            "toxicity_score": 0.95, "sentiment_score": -0.98,
            "has_urls": False, "caps_ratio": 0.05
        },
        "expected_action": 3,  # ban — severe harassment, chronic offender
        "label": "severe_harassment",
    },
    {
        "id": "med_008",
        "post_text": "Can someone help me understand how cryptocurrency taxes work in India?",
        "user_history": {"account_age_days": 300, "previous_violations": 0, "post_count": 120},
        "context": {"platform": "forum", "post_type": "post", "reported": False},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": False,
            "toxicity_score": 0.01, "sentiment_score": 0.1,
            "has_urls": False, "caps_ratio": 0.02
        },
        "expected_action": 0,  # allow — genuine question
        "label": "safe",
    },
    {
        "id": "med_009",
        "post_text": "Shut up you moron. Nobody cares about your stupid opinion here.",
        "user_history": {"account_age_days": 150, "previous_violations": 2, "post_count": 200},
        "context": {"platform": "forum", "post_type": "comment", "reported": True},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": True,
            "toxicity_score": 0.68, "sentiment_score": -0.8,
            "has_urls": False, "caps_ratio": 0.05
        },
        "expected_action": 2,  # remove — aggressive personal attack
        "label": "offensive",
    },
    {
        "id": "med_010",
        "post_text": "Your cooking looks absolutely disgusting. How do you even eat that garbage.",
        "user_history": {"account_age_days": 220, "previous_violations": 1, "post_count": 170},
        "context": {"platform": "social_media", "post_type": "comment", "reported": True},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": True,
            "toxicity_score": 0.5, "sentiment_score": -0.75,
            "has_urls": False, "caps_ratio": 0.03
        },
        "expected_action": 1,  # warn — rude but mild, first-ish offense
        "label": "mild_offensive",
    },
    {
        "id": "med_011",
        "post_text": "Women should stay home and not have opinions on politics. It's not their domain.",
        "user_history": {"account_age_days": 180, "previous_violations": 2, "post_count": 130},
        "context": {"platform": "forum", "post_type": "post", "reported": True},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": False,
            "toxicity_score": 0.78, "sentiment_score": -0.6,
            "has_urls": False, "caps_ratio": 0.03
        },
        "expected_action": 2,  # remove — sexist hate speech
        "label": "hate_speech",
    },
    {
        "id": "med_012",
        "post_text": "I think the author's argument is flawed and here's why — thread below 👇",
        "user_history": {"account_age_days": 1100, "previous_violations": 0, "post_count": 750},
        "context": {"platform": "forum", "post_type": "post", "reported": False},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": False,
            "toxicity_score": 0.06, "sentiment_score": -0.1,
            "has_urls": False, "caps_ratio": 0.02
        },
        "expected_action": 0,  # allow — intellectual critique
        "label": "safe",
    },
    {
        "id": "med_013",
        "post_text": "What an ugly profile picture lol, did a donkey take that photo?",
        "user_history": {"account_age_days": 80, "previous_violations": 1, "post_count": 55},
        "context": {"platform": "social_media", "post_type": "comment", "reported": True},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": True,
            "toxicity_score": 0.55, "sentiment_score": -0.7,
            "has_urls": False, "caps_ratio": 0.03
        },
        "expected_action": 1,  # warn — personal mockery but mild
        "label": "mild_offensive",
    },
    {
        "id": "med_014",
        "post_text": "People with this political view are mentally ill and dangerous to society.",
        "user_history": {"account_age_days": 95, "previous_violations": 3, "post_count": 70},
        "context": {"platform": "forum", "post_type": "post", "reported": True},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": True,
            "toxicity_score": 0.82, "sentiment_score": -0.85,
            "has_urls": False, "caps_ratio": 0.03
        },
        "expected_action": 2,  # remove — dehumanizing hate speech
        "label": "hate_speech",
    },
    {
        "id": "med_015",
        "post_text": "I strongly oppose this community's moderation team. Very biased decisions.",
        "user_history": {"account_age_days": 500, "previous_violations": 0, "post_count": 290},
        "context": {"platform": "forum", "post_type": "post", "reported": False},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": False,
            "toxicity_score": 0.2, "sentiment_score": -0.4,
            "has_urls": False, "caps_ratio": 0.03
        },
        "expected_action": 0,  # allow — platform criticism is valid speech
        "label": "safe",
    },
]
