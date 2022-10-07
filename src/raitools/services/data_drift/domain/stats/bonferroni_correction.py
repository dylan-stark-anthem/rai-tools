"""Bonferroni correction."""


def bonferroni_correction(num_features: int, alpha: float) -> float:
    """Calculates Bonferroni correction for given number of features."""
    return alpha / num_features
