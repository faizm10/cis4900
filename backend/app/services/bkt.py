"""
Bayesian Knowledge Tracing (BKT) implementation.

Four parameters per KC:
  P(L0): prior probability of already knowing the skill
  P(T):  probability of learning the skill per attempt (transition)
  P(G):  probability of correct response by guessing (without knowing)
  P(S):  probability of incorrect response despite knowing (slip)

Reference: Corbett & Anderson (1995)
"""

TAU_MASTERY = 0.95   # threshold to consider KC mastered → advance
TAU_LOW = 0.40       # threshold below which mastery is considered stuck → reroute
K_REROUTE = 3        # minimum attempts before reroute is eligible


def bkt_update(p_l: float, correct: bool, p_t: float, p_g: float, p_s: float) -> float:
    """
    Update P(L) after a single observation.

    Returns the updated mastery probability P(L_t).
    """
    if correct:
        # Learner answered correctly: update P(L | correct)
        numerator = p_l * (1.0 - p_s)
        denominator = numerator + (1.0 - p_l) * p_g
    else:
        # Learner answered incorrectly: update P(L | incorrect)
        numerator = p_l * p_s
        denominator = numerator + (1.0 - p_l) * (1.0 - p_g)

    # Guard against division by zero (degenerate parameters)
    if denominator == 0.0:
        p_l_given_obs = p_l
    else:
        p_l_given_obs = numerator / denominator

    # Apply learning transition: learner may have acquired knowledge this attempt
    p_l_next = p_l_given_obs + (1.0 - p_l_given_obs) * p_t
    return float(p_l_next)


def decide(p_mastery_after: float, attempt_count: int) -> str:
    """
    Determine the next instructional action based on updated mastery.

    Returns: "advance" | "remediate" | "reroute"
    """
    if p_mastery_after >= TAU_MASTERY:
        return "advance"
    if p_mastery_after < TAU_LOW and attempt_count >= K_REROUTE:
        return "reroute"
    return "remediate"
