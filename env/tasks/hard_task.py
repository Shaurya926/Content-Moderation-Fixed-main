"""
hard_task.py — Context-Based Moderation (Hard Difficulty)
15 highly nuanced samples. Agent must understand:
  - Sarcasm that looks offensive but isn't
  - Political debate that looks like hate but is legitimate
  - Genuinely harmful content that looks polite
  - Dark humor vs real threats
Over-blocking (removing safe content) and under-blocking (missing harm) are both penalized.
"""

HARD_SAMPLES = [
    {
        "id": "hard_001",
        "post_text": "Oh great, another 'expert' on the internet who knows everything about medicine 🙄",
        "user_history": {"account_age_days": 800, "previous_violations": 0, "post_count": 500},
        "context": {"platform": "forum", "post_type": "comment", "reported": True},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": False,
            "toxicity_score": 0.3, "sentiment_score": -0.4,
            "has_urls": False, "caps_ratio": 0.03
        },
        "expected_action": 0,  # allow — clear sarcasm, no actual harm
        "label": "sarcasm_safe",
    },
    {
        "id": "hard_002",
        "post_text": "I think we should seriously reconsider whether certain communities are compatible with modern democratic values.",
        "user_history": {"account_age_days": 200, "previous_violations": 1, "post_count": 100},
        "context": {"platform": "forum", "post_type": "post", "reported": True},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": False,
            "toxicity_score": 0.4, "sentiment_score": -0.2,
            "has_urls": False, "caps_ratio": 0.02
        },
        "expected_action": 1,  # warn — coded hate speech, borderline
        "label": "borderline_hate",
    },
    {
        "id": "hard_003",
        "post_text": "This neighborhood has really gone downhill since 'certain people' moved in, if you know what I mean.",
        "user_history": {"account_age_days": 350, "previous_violations": 2, "post_count": 180},
        "context": {"platform": "social_media", "post_type": "post", "reported": True},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": False,
            "toxicity_score": 0.55, "sentiment_score": -0.35,
            "has_urls": False, "caps_ratio": 0.03
        },
        "expected_action": 2,  # remove — veiled racist dog whistle
        "label": "coded_hate",
    },
    {
        "id": "hard_004",
        "post_text": "I'm so tired of this job I could scream. My boss is driving me absolutely insane 😤",
        "user_history": {"account_age_days": 1000, "previous_violations": 0, "post_count": 650},
        "context": {"platform": "social_media", "post_type": "post", "reported": False},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": False,
            "toxicity_score": 0.22, "sentiment_score": -0.6,
            "has_urls": False, "caps_ratio": 0.04
        },
        "expected_action": 0,  # allow — workplace frustration, normal expression
        "label": "safe_frustration",
    },
    {
        "id": "hard_005",
        "post_text": "I don't mean to be rude, but people who support this policy must not have done basic research.",
        "user_history": {"account_age_days": 600, "previous_violations": 0, "post_count": 400},
        "context": {"platform": "forum", "post_type": "comment", "reported": False},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": False,
            "toxicity_score": 0.28, "sentiment_score": -0.3,
            "has_urls": False, "caps_ratio": 0.02
        },
        "expected_action": 0,  # allow — strong opinion, not targeted hate
        "label": "safe_opinion",
    },
    {
        "id": "hard_006",
        "post_text": "Haha don't worry about me, I'll just disappear one day and nobody will notice 😅",
        "user_history": {"account_age_days": 30, "previous_violations": 0, "post_count": 15},
        "context": {"platform": "social_media", "post_type": "post", "reported": True},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": False,
            "toxicity_score": 0.2, "sentiment_score": -0.5,
            "has_urls": False, "caps_ratio": 0.03
        },
        "expected_action": 1,  # warn — possible mental health signal with humor mask
        "label": "self_harm_signal",
    },
    {
        "id": "hard_007",
        "post_text": "The only good solution to this political problem is to eliminate the opposition. History shows this works.",
        "user_history": {"account_age_days": 250, "previous_violations": 2, "post_count": 140},
        "context": {"platform": "forum", "post_type": "post", "reported": True},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": False,
            "toxicity_score": 0.65, "sentiment_score": -0.3,
            "has_urls": False, "caps_ratio": 0.03
        },
        "expected_action": 2,  # remove — incitement veiled in political language
        "label": "incitement",
    },
    {
        "id": "hard_008",
        "post_text": "Yeah sure, because THAT will definitely solve climate change 🙄 Keep dreaming.",
        "user_history": {"account_age_days": 700, "previous_violations": 0, "post_count": 430},
        "context": {"platform": "social_media", "post_type": "comment", "reported": True},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": False,
            "toxicity_score": 0.25, "sentiment_score": -0.45,
            "has_urls": False, "caps_ratio": 0.1
        },
        "expected_action": 0,  # allow — sarcasm in policy debate, not harmful
        "label": "sarcasm_safe",
    },
    {
        "id": "hard_009",
        "post_text": "We should organize and make sure these people never feel comfortable in our online spaces.",
        "user_history": {"account_age_days": 120, "previous_violations": 3, "post_count": 85},
        "context": {"platform": "forum", "post_type": "post", "reported": True},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": False,
            "toxicity_score": 0.6, "sentiment_score": -0.4,
            "has_urls": False, "caps_ratio": 0.02
        },
        "expected_action": 2,  # remove — coordinated harassment campaign call
        "label": "coordinated_harassment",
    },
    {
        "id": "hard_010",
        "post_text": "My parents are so annoying sometimes. I wish they'd just leave me alone for one day!",
        "user_history": {"account_age_days": 450, "previous_violations": 0, "post_count": 260},
        "context": {"platform": "social_media", "post_type": "post", "reported": False},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": False,
            "toxicity_score": 0.12, "sentiment_score": -0.4,
            "has_urls": False, "caps_ratio": 0.02
        },
        "expected_action": 0,  # allow — normal teen/adult family frustration
        "label": "safe_frustration",
    },
    {
        "id": "hard_011",
        "post_text": "I've been researching the most effective methods. I think I've finally found the answer to end it all.",
        "user_history": {"account_age_days": 20, "previous_violations": 0, "post_count": 8},
        "context": {"platform": "social_media", "post_type": "post", "reported": True},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": False,
            "toxicity_score": 0.35, "sentiment_score": -0.6,
            "has_urls": False, "caps_ratio": 0.02
        },
        "expected_action": 1,  # warn — ambiguous but high-risk self harm language
        "label": "self_harm_signal",
    },
    {
        "id": "hard_012",
        "post_text": "Honestly speaking, if you can't handle criticism, maybe public life isn't for you.",
        "user_history": {"account_age_days": 900, "previous_violations": 0, "post_count": 560},
        "context": {"platform": "forum", "post_type": "comment", "reported": False},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": False,
            "toxicity_score": 0.2, "sentiment_score": -0.25,
            "has_urls": False, "caps_ratio": 0.02
        },
        "expected_action": 0,  # allow — direct but not abusive commentary
        "label": "safe_opinion",
    },
    {
        "id": "hard_013",
        "post_text": "People who think like you are the reason this country is failing. You all deserve what's coming.",
        "user_history": {"account_age_days": 160, "previous_violations": 4, "post_count": 110},
        "context": {"platform": "forum", "post_type": "comment", "reported": True},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": False,
            "toxicity_score": 0.75, "sentiment_score": -0.8,
            "has_urls": False, "caps_ratio": 0.03
        },
        "expected_action": 2,  # remove — threatening + dehumanizing
        "label": "threat",
    },
    {
        "id": "hard_014",
        "post_text": "It's funny how quickly society forgets these people exist until they need something from them.",
        "user_history": {"account_age_days": 1200, "previous_violations": 0, "post_count": 800},
        "context": {"platform": "forum", "post_type": "post", "reported": False},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": False,
            "toxicity_score": 0.15, "sentiment_score": -0.2,
            "has_urls": False, "caps_ratio": 0.02
        },
        "expected_action": 0,  # allow — social commentary, not hate
        "label": "safe_commentary",
    },
    {
        "id": "hard_015",
        "post_text": "Since nobody here respects my views, I guess I'll just take matters into my own hands. Watch this space.",
        "user_history": {"account_age_days": 75, "previous_violations": 5, "post_count": 50},
        "context": {"platform": "forum", "post_type": "post", "reported": True},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": False,
            "toxicity_score": 0.55, "sentiment_score": -0.55,
            "has_urls": False, "caps_ratio": 0.04
        },
        "expected_action": 2,  # remove — veiled threat, prior violations, alarming
        "label": "veiled_threat",
    },
]
