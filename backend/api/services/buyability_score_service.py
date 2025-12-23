"""
Buyability Score Service

Calculates a comprehensive buyability score by combining:
- Statistical Health Score (ML-based)
- Mechanical Reliability Score (LLM-based)
- Crash/Paint Score (Rule-based)

Formula (Hybrid Approach):
1. Weighted average: S*0.25 + M*0.40 + C*0.35
2. Minimum pull: blend with min_score (alpha=0.30)
3. Geometric mean dampener: penalize imbalance (beta=0.05)
4. Critical failure penalties based on thresholds
5. Tier labels for UX (KACIN, RISKLI, GUVENLI)
"""

from typing import Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import math


class BuyabilityTier(str, Enum):
    """Buyability tier classification"""
    KACIN = "KACIN"           # Avoid - critical issues
    RISKLI = "RISKLI"         # Risky - serious concerns
    DIKKAT = "DIKKAT"         # Caution - moderate concerns
    NORMAL = "NORMAL"         # Normal - acceptable
    GUVENLI = "GUVENLI"       # Safe - good condition


@dataclass
class BuyabilityScoreResult:
    """Result of buyability score calculation"""
    final_score: int                    # 0-100 final score
    tier: BuyabilityTier                # Classification tier
    tier_label_tr: str                  # Turkish label for tier

    # Component scores (for transparency)
    statistical_score: Optional[int]    # S: ML-based health score
    mechanical_score: Optional[int]     # M: LLM-based reliability score
    crash_score: Optional[int]          # C: Rule-based damage score

    # Calculation breakdown
    weighted_average: float             # Base weighted average
    min_score: int                      # Minimum of available scores
    blended_score: float                # After min pull and GM dampener
    penalty_applied: int                # Penalty points deducted
    bonus_applied: int                  # Bonus points added (for safe cars)

    # Explanation
    calculation_summary: str            # Human-readable summary
    warning_message: Optional[str]      # Warning if any score is critically low


# Configuration constants (tunable)
WEIGHT_STATISTICAL = 0.25   # Weight for ML-based statistical score
WEIGHT_MECHANICAL = 0.40    # Weight for LLM-based mechanical score
WEIGHT_CRASH = 0.35         # Weight for crash/paint score

ALPHA = 0.30                # How much min_score pulls the result
BETA = 0.05                 # Weight for geometric mean dampener

THRESHOLD_CRITICAL = 25     # Below this = critical failure
THRESHOLD_SERIOUS = 40      # Below this = serious concern
THRESHOLD_CAUTION = 50      # Below this = caution

PENALTY_CRITICAL = 25       # Penalty for critical failure
PENALTY_SERIOUS = 12        # Penalty for serious concern
PENALTY_CAUTION = 5         # Penalty for caution

BONUS_SAFE = 5              # Bonus for all scores >= 70
SAFE_THRESHOLD = 70         # Threshold for "safe" classification


def calculate_buyability_score(
    statistical_score: Optional[int],
    mechanical_score: Optional[int],
    crash_score: Optional[int]
) -> BuyabilityScoreResult:
    """
    Calculate comprehensive buyability score from three component scores.

    Args:
        statistical_score: ML-based health score (0-100), None if unavailable
        mechanical_score: LLM-based reliability score (0-100), None if unavailable
        crash_score: Rule-based damage score (0-100), None if unavailable

    Returns:
        BuyabilityScoreResult with final score and breakdown
    """

    # Collect available scores
    available_scores = []
    if statistical_score is not None:
        available_scores.append(('statistical', statistical_score, WEIGHT_STATISTICAL))
    if mechanical_score is not None:
        available_scores.append(('mechanical', mechanical_score, WEIGHT_MECHANICAL))
    if crash_score is not None:
        available_scores.append(('crash', crash_score, WEIGHT_CRASH))

    # Handle edge case: no scores available
    if not available_scores:
        return BuyabilityScoreResult(
            final_score=0,
            tier=BuyabilityTier.KACIN,
            tier_label_tr="Analiz Yapilamadi",
            statistical_score=None,
            mechanical_score=None,
            crash_score=None,
            weighted_average=0,
            min_score=0,
            blended_score=0,
            penalty_applied=0,
            bonus_applied=0,
            calculation_summary="Hicbir skor mevcut degil.",
            warning_message="Analiz icin yeterli veri yok."
        )

    # Normalize weights if some scores are missing
    total_weight = sum(w for _, _, w in available_scores)
    normalized_scores = [(name, score, weight / total_weight) for name, score, weight in available_scores]

    # Step 1: Calculate weighted average
    weighted_avg = sum(score * norm_weight for _, score, norm_weight in normalized_scores)

    # Step 2: Find minimum score
    min_score = min(score for _, score, _ in available_scores)

    # Step 3: Blend with minimum (pull toward min_score)
    base = weighted_avg * (1 - ALPHA) + min_score * ALPHA

    # Step 4: Apply geometric mean dampener (only if we have multiple scores)
    if len(available_scores) >= 2:
        # Geometric mean of available scores
        product = 1
        for _, score, _ in available_scores:
            # Add small epsilon to avoid log(0) issues
            product *= max(score, 0.1)
        gm = product ** (1 / len(available_scores))
        blended = base * (1 - BETA) + gm * BETA
    else:
        gm = available_scores[0][1]  # Single score, GM is the score itself
        blended = base

    # Step 5: Apply critical failure penalties
    penalty = 0
    if min_score <= THRESHOLD_CRITICAL:
        penalty = PENALTY_CRITICAL
    elif min_score <= THRESHOLD_SERIOUS:
        penalty = PENALTY_SERIOUS
    elif min_score <= THRESHOLD_CAUTION:
        penalty = PENALTY_CAUTION

    # Step 6: Determine tier and apply bonus
    bonus = 0
    all_scores_safe = all(score >= SAFE_THRESHOLD for _, score, _ in available_scores)

    if min_score <= THRESHOLD_CRITICAL:
        tier = BuyabilityTier.KACIN
        tier_label_tr = "KACIN - Ciddi Sorunlar Var"
    elif min_score <= THRESHOLD_SERIOUS:
        tier = BuyabilityTier.RISKLI
        tier_label_tr = "RISKLI - Dikkatli Inceleme Gerekli"
    elif min_score <= THRESHOLD_CAUTION:
        tier = BuyabilityTier.DIKKAT
        tier_label_tr = "DIKKAT - Bazi Endiseler Var"
    elif all_scores_safe:
        tier = BuyabilityTier.GUVENLI
        tier_label_tr = "GUVENLI - Iyi Durumda"
        bonus = BONUS_SAFE
    else:
        tier = BuyabilityTier.NORMAL
        tier_label_tr = "NORMAL - Kabul Edilebilir"

    # Calculate final score
    final_score = blended - penalty + bonus

    # Enforce bounds and tier caps
    if tier == BuyabilityTier.KACIN:
        final_score = min(final_score, 30)  # Cap at 30 for KACIN
    elif tier == BuyabilityTier.RISKLI:
        final_score = min(final_score, 50)  # Cap at 50 for RISKLI

    final_score = max(0, min(100, round(final_score)))  # Clamp to 0-100

    # Generate warning message
    warning_message = None
    if min_score <= THRESHOLD_CRITICAL:
        # Find which score is critically low
        critical_scores = [name for name, score, _ in available_scores if score <= THRESHOLD_CRITICAL]
        score_names_tr = {
            'statistical': 'Istatistiksel Skor',
            'mechanical': 'Mekanik Skor',
            'crash': 'Hasar Skoru'
        }
        critical_names = [score_names_tr.get(s, s) for s in critical_scores]
        warning_message = f"Kritik uyari: {', '.join(critical_names)} cok dusuk!"
    elif min_score <= THRESHOLD_SERIOUS:
        warning_message = "Dikkat: Bazi skorlar endise verici seviyede."

    # Generate calculation summary
    score_parts = []
    if statistical_score is not None:
        score_parts.append(f"S={statistical_score}")
    if mechanical_score is not None:
        score_parts.append(f"M={mechanical_score}")
    if crash_score is not None:
        score_parts.append(f"C={crash_score}")

    calculation_summary = (
        f"Skorlar: {', '.join(score_parts)} | "
        f"Agirlikli Ort: {weighted_avg:.1f} | "
        f"Min: {min_score} | "
        f"Karisik: {blended:.1f} | "
        f"Ceza: -{penalty} | "
        f"Bonus: +{bonus} | "
        f"Sonuc: {final_score}"
    )

    return BuyabilityScoreResult(
        final_score=final_score,
        tier=tier,
        tier_label_tr=tier_label_tr,
        statistical_score=statistical_score,
        mechanical_score=mechanical_score,
        crash_score=crash_score,
        weighted_average=round(weighted_avg, 2),
        min_score=min_score,
        blended_score=round(blended, 2),
        penalty_applied=penalty,
        bonus_applied=bonus,
        calculation_summary=calculation_summary,
        warning_message=warning_message
    )


def buyability_score_to_dict(result: BuyabilityScoreResult) -> dict:
    """Convert BuyabilityScoreResult to dictionary for API response"""
    return {
        "final_score": result.final_score,
        "tier": result.tier.value,
        "tier_label_tr": result.tier_label_tr,
        "component_scores": {
            "statistical": result.statistical_score,
            "mechanical": result.mechanical_score,
            "crash": result.crash_score
        },
        "calculation_breakdown": {
            "weighted_average": result.weighted_average,
            "min_score": result.min_score,
            "blended_score": result.blended_score,
            "penalty_applied": result.penalty_applied,
            "bonus_applied": result.bonus_applied
        },
        "calculation_summary": result.calculation_summary,
        "warning_message": result.warning_message
    }
