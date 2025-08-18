"""
Simplest TraiGent Demo - No Path Hacks!

Run from project root:
    python -m demos.quickstart.simple_demo
"""

import traigent


@traigent.optimize(
    config_space={"temperature": [0.0, 0.5, 1.0]},
    objective="maximize:accuracy",
    mode="local",
)
def classify_sentiment(text: str, temperature: float = 0.5) -> str:
    """Simple sentiment classifier."""
    # Mock implementation for demo
    if "love" in text.lower() or "great" in text.lower():
        return "positive"
    elif "hate" in text.lower() or "terrible" in text.lower():
        return "negative"
    return "neutral"


def main() -> None:
    print("✅ TraiGent Simple Demo")
    print("=" * 40)

    # Test without optimization
    result = classify_sentiment("I love this!")
    print(f"Result: {result}")


if __name__ == "__main__":
    main()
