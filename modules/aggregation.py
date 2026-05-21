import numpy as np


def compute_final_trust(direct_trust, indirect_trust, alpha=0.6):
    """
    Compute final trust score using weighted aggregation.

    FT(u, s) = alpha * DT(u, s) + beta * IT(u, s)
    where beta = 1 - alpha.
    """

    if alpha < 0 or alpha > 1:
        raise ValueError("alpha must be between 0 and 1")

    beta = 1 - alpha

    direct_trust = 0.0 if direct_trust is None else direct_trust
    indirect_trust = 0.0 if indirect_trust is None else indirect_trust

    final_trust = alpha * direct_trust + beta * indirect_trust

    return float(np.clip(final_trust, 0, 1))


def trust_decision(final_trust, trust_threshold=0.60):
    """
    Apply trust threshold decision.
    """

    if final_trust >= trust_threshold:
        return "Trusted"

    return "Low Trust"
