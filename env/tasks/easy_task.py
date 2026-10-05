"""
easy_task.py — Spam Detection Task (Easy Difficulty)
15 samples with obvious spam signals: fake prizes, clickbait, phishing links.
Expected action: 2 (remove) for spam, 0 (allow) for legitimate posts.
"""

EASY_SAMPLES = [
    {
        "id": "easy_001",
        "post_text": "🎉🎉 WINNER ALERT! Click here to claim your ₹10,000 prize NOW!!! Limited time!!!",
        "user_history": {"account_age_days": 1, "previous_violations": 5, "post_count": 8},
        "context": {"platform": "social_media", "post_type": "post", "reported": True},
        "extracted_features": {
            "has_spam_keywords": True, "has_offensive_words": False,
            "toxicity_score": 0.1, "sentiment_score": 0.8,
            "has_urls": True, "caps_ratio": 0.45
        },
        "expected_action": 2,
        "label": "spam",
    },
    {
        "id": "easy_002",
        "post_text": "Just had an amazing trip to Manali! The mountains were breathtaking 🏔️",
        "user_history": {"account_age_days": 730, "previous_violations": 0, "post_count": 342},
        "context": {"platform": "social_media", "post_type": "post", "reported": False},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": False,
            "toxicity_score": 0.02, "sentiment_score": 0.9,
            "has_urls": False, "caps_ratio": 0.05
        },
        "expected_action": 0,
        "label": "safe",
    },
    {
        "id": "easy_003",
        "post_text": "FREE IPHONE 15!!! CLICK LINK IN BIO!!! HURRY ONLY 10 LEFT!!!",
        "user_history": {"account_age_days": 3, "previous_violations": 2, "post_count": 15},
        "context": {"platform": "social_media", "post_type": "comment", "reported": True},
        "extracted_features": {
            "has_spam_keywords": True, "has_offensive_words": False,
            "toxicity_score": 0.05, "sentiment_score": 0.6,
            "has_urls": True, "caps_ratio": 0.85
        },
        "expected_action": 2,
        "label": "spam",
    },
    {
        "id": "easy_004",
        "post_text": "Happy birthday to my best friend! Wishing you all the happiness 🎂❤️",
        "user_history": {"account_age_days": 450, "previous_violations": 0, "post_count": 210},
        "context": {"platform": "social_media", "post_type": "post", "reported": False},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": False,
            "toxicity_score": 0.01, "sentiment_score": 0.95,
            "has_urls": False, "caps_ratio": 0.03
        },
        "expected_action": 0,
        "label": "safe",
    },
    {
        "id": "easy_005",
        "post_text": "Earn ₹5000 daily from home! No investment needed! DM me now!!! 100% genuine!!!",
        "user_history": {"account_age_days": 7, "previous_violations": 3, "post_count": 22},
        "context": {"platform": "social_media", "post_type": "comment", "reported": True},
        "extracted_features": {
            "has_spam_keywords": True, "has_offensive_words": False,
            "toxicity_score": 0.08, "sentiment_score": 0.7,
            "has_urls": False, "caps_ratio": 0.25
        },
        "expected_action": 2,
        "label": "spam",
    },
    {
        "id": "easy_006",
        "post_text": "Anyone else obsessed with the new season of Mirzapur? That ending!! 😱",
        "user_history": {"account_age_days": 900, "previous_violations": 0, "post_count": 500},
        "context": {"platform": "social_media", "post_type": "post", "reported": False},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": False,
            "toxicity_score": 0.05, "sentiment_score": 0.4,
            "has_urls": False, "caps_ratio": 0.04
        },
        "expected_action": 0,
        "label": "safe",
    },
    {
        "id": "easy_007",
        "post_text": "VIRUS ALERT! Your phone is infected! Download our cleaner app NOW: bit.ly/clnr",
        "user_history": {"account_age_days": 2, "previous_violations": 4, "post_count": 9},
        "context": {"platform": "social_media", "post_type": "comment", "reported": True},
        "extracted_features": {
            "has_spam_keywords": True, "has_offensive_words": False,
            "toxicity_score": 0.2, "sentiment_score": -0.3,
            "has_urls": True, "caps_ratio": 0.4
        },
        "expected_action": 2,
        "label": "spam",
    },
    {
        "id": "easy_008",
        "post_text": "Cooked dal makhani for the first time and it turned out perfectly! Recipe in comments.",
        "user_history": {"account_age_days": 600, "previous_violations": 0, "post_count": 180},
        "context": {"platform": "social_media", "post_type": "post", "reported": False},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": False,
            "toxicity_score": 0.01, "sentiment_score": 0.85,
            "has_urls": False, "caps_ratio": 0.02
        },
        "expected_action": 0,
        "label": "safe",
    },
    {
        "id": "easy_009",
        "post_text": "You have been selected for KBC! Call this number 9XXXXXXX to claim ₹25 lakh!",
        "user_history": {"account_age_days": 5, "previous_violations": 6, "post_count": 18},
        "context": {"platform": "social_media", "post_type": "dm", "reported": True},
        "extracted_features": {
            "has_spam_keywords": True, "has_offensive_words": False,
            "toxicity_score": 0.1, "sentiment_score": 0.5,
            "has_urls": False, "caps_ratio": 0.1
        },
        "expected_action": 2,
        "label": "spam",
    },
    {
        "id": "easy_010",
        "post_text": "Cricket match today was incredible! India won by 6 wickets. JADEJA THE GOAT! 🏏",
        "user_history": {"account_age_days": 1200, "previous_violations": 0, "post_count": 800},
        "context": {"platform": "social_media", "post_type": "post", "reported": False},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": False,
            "toxicity_score": 0.02, "sentiment_score": 0.9,
            "has_urls": False, "caps_ratio": 0.12
        },
        "expected_action": 0,
        "label": "safe",
    },
    {
        "id": "easy_011",
        "post_text": "BUY FOLLOWERS CHEAP! 1000 followers = ₹50 only! Instant delivery! DM NOW!!!",
        "user_history": {"account_age_days": 10, "previous_violations": 2, "post_count": 30},
        "context": {"platform": "social_media", "post_type": "comment", "reported": True},
        "extracted_features": {
            "has_spam_keywords": True, "has_offensive_words": False,
            "toxicity_score": 0.15, "sentiment_score": 0.3,
            "has_urls": False, "caps_ratio": 0.5
        },
        "expected_action": 2,
        "label": "spam",
    },
    {
        "id": "easy_012",
        "post_text": "Really excited about my sister's wedding next week! Lots of preparations going on 🎊",
        "user_history": {"account_age_days": 800, "previous_violations": 0, "post_count": 420},
        "context": {"platform": "social_media", "post_type": "post", "reported": False},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": False,
            "toxicity_score": 0.01, "sentiment_score": 0.92,
            "has_urls": False, "caps_ratio": 0.02
        },
        "expected_action": 0,
        "label": "safe",
    },
    {
        "id": "easy_013",
        "post_text": "MAKE MONEY FAST!! Join our MLM network. Refer 5 friends get ₹500 each! Zero risk!",
        "user_history": {"account_age_days": 15, "previous_violations": 1, "post_count": 45},
        "context": {"platform": "social_media", "post_type": "post", "reported": True},
        "extracted_features": {
            "has_spam_keywords": True, "has_offensive_words": False,
            "toxicity_score": 0.1, "sentiment_score": 0.6,
            "has_urls": False, "caps_ratio": 0.35
        },
        "expected_action": 2,
        "label": "spam",
    },
    {
        "id": "easy_014",
        "post_text": "Finally finished my MBA! Grateful to my professors and family. Onward! 🎓",
        "user_history": {"account_age_days": 1500, "previous_violations": 0, "post_count": 950},
        "context": {"platform": "social_media", "post_type": "post", "reported": False},
        "extracted_features": {
            "has_spam_keywords": False, "has_offensive_words": False,
            "toxicity_score": 0.01, "sentiment_score": 0.95,
            "has_urls": False, "caps_ratio": 0.04
        },
        "expected_action": 0,
        "label": "safe",
    },
    {
        "id": "easy_015",
        "post_text": "Lottery WINNER! Your number is selected! Send ₹500 processing fee to claim ₹1 crore!",
        "user_history": {"account_age_days": 4, "previous_violations": 7, "post_count": 12},
        "context": {"platform": "social_media", "post_type": "dm", "reported": True},
        "extracted_features": {
            "has_spam_keywords": True, "has_offensive_words": False,
            "toxicity_score": 0.12, "sentiment_score": 0.4,
            "has_urls": False, "caps_ratio": 0.25
        },
        "expected_action": 2,
        "label": "spam",
    },
]
