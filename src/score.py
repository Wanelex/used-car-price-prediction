"""
Risk Score Utility Functions

Provides text descriptions for buyability risk scores (0-100).
Higher score = lower risk = safer to buy.
"""


def risk_score_to_text(score: int) -> str:
    """
    Convert risk score (0-100) to descriptive text.

    Args:
        score: Risk score from 0 to 100
               Higher score = safer to buy

    Returns:
        Human-readable description of the risk level
    """
    if score >= 86:
        return "Minimal risk - Excellent condition vehicle"
    elif score >= 71:
        return "Very low risk - Good condition vehicle"
    elif score >= 51:
        return "Low risk - Generally acceptable condition"
    elif score >= 31:
        return "Moderate risk - Some concerns, thorough inspection recommended"
    else:
        return "High risk - Multiple concerns with vehicle condition"


def risk_score_to_recommendation(score: int) -> str:
    """
    Convert risk score to a buying recommendation.

    Args:
        score: Risk score from 0 to 100

    Returns:
        Buying recommendation string
    """
    if score >= 71:
        return "Recommended - This vehicle appears to be in good condition"
    elif score >= 51:
        return "Consider - Acceptable condition, but verify with inspection"
    elif score >= 31:
        return "Caution - Multiple factors require attention"
    else:
        return "Not Recommended - Significant concerns detected"


def get_risk_level(score: int) -> str:
    """
    Get risk level category.

    Args:
        score: Risk score from 0 to 100

    Returns:
        Risk level category (MINIMAL, LOW, MODERATE, HIGH)
    """
    if score >= 71:
        return "MINIMAL"
    elif score >= 51:
        return "LOW"
    elif score >= 31:
        return "MODERATE"
    else:
        return "HIGH"


# Legacy function for backwards compatibility
def score_to_text(cls):
    """
    Legacy function - maps old 0-4 scores to text.
    Consider using risk_score_to_text() instead for new code.
    """
    messages = {
        0: "High risk - Multiple concerns with vehicle condition",
        1: "Moderate risk - Some concerns, thorough inspection recommended",
        2: "Low risk - Generally acceptable condition",
        3: "Very low risk - Good condition vehicle",
        4: "Minimal risk - Excellent condition vehicle"
    }
    return messages.get(cls, "Unknown")
