import numpy as np
import pandas as pd


def detect_extreme_deviation_users(
    rating_matrix,
    baseline_matrix,
    deviation_threshold=0.35,
    ratio_threshold=0.60,
    min_ratings=5
):
    """
    Detect users whose attacked ratings strongly differ from their clean baseline ratings.
    """
    flagged_users = []

    for user_id in rating_matrix.index:
        current_ratings = rating_matrix.loc[user_id]
        baseline_ratings = baseline_matrix.loc[user_id]

        valid = current_ratings.notna() & baseline_ratings.notna()

        if valid.sum() < min_ratings:
            continue

        deviation = (current_ratings[valid] - baseline_ratings[valid]).abs()
        high_deviation_ratio = (deviation >= deviation_threshold).mean()

        if high_deviation_ratio >= ratio_threshold:
            flagged_users.append(user_id)

    return set(flagged_users)


def cusum_user_anomaly(deviations, drift=0.02, threshold=5.00):
    """
    Apply CUSUM anomaly detection to one user's deviation sequence.
    """
    positive_sum = 0.0
    negative_sum = 0.0

    for deviation in deviations:
        positive_sum = max(0, positive_sum + deviation - drift)
        negative_sum = min(0, negative_sum + deviation + drift)

        if positive_sum > threshold or abs(negative_sum) > threshold:
            return True

    return False


def detect_cusum_users(
    rating_matrix,
    baseline_matrix,
    drift=0.02,
    threshold=5.00,
    min_ratings=5
):
    """
    Detect users with abnormal rating changes using CUSUM.
    """
    flagged_users = []

    for user_id in rating_matrix.index:
        current_ratings = rating_matrix.loc[user_id]
        baseline_ratings = baseline_matrix.loc[user_id]

        valid = current_ratings.notna() & baseline_ratings.notna()

        if valid.sum() < min_ratings:
            continue

        deviations = (current_ratings[valid] - baseline_ratings[valid]).values

        is_anomalous = cusum_user_anomaly(
            deviations=deviations,
            drift=drift,
            threshold=threshold
        )

        if is_anomalous:
            flagged_users.append(user_id)

    return set(flagged_users)


def detect_low_trust_users(final_trust_df, trust_threshold=0.60):
    """
    Detect user-service interactions where final trust is below threshold.
    """
    low_trust_rows = final_trust_df[
        final_trust_df["final_trust"] < trust_threshold
    ].copy()

    low_trust_users = set(low_trust_rows["user_id"].unique())

    return low_trust_users, low_trust_rows


def combine_flagged_users(*flagged_sets):
    """
    Combine multiple flagged-user sets.
    """
    combined = set()

    for flagged in flagged_sets:
        combined.update(flagged)

    return combined


def detection_rate(true_malicious_users, flagged_users):
    """
    Detection Rate = correctly flagged malicious users / total malicious users.
    """
    true_malicious_users = set(true_malicious_users)
    flagged_users = set(flagged_users)

    if len(true_malicious_users) == 0:
        return 0.0

    correctly_detected = true_malicious_users.intersection(flagged_users)

    return len(correctly_detected) / len(true_malicious_users)


def false_positive_rate(true_malicious_users, flagged_users, total_users):
    """
    False Positive Rate = normal users incorrectly flagged / total normal users.
    """
    true_malicious_users = set(true_malicious_users)
    flagged_users = set(flagged_users)

    all_users = set(range(total_users))
    legitimate_users = all_users - true_malicious_users

    if len(legitimate_users) == 0:
        return 0.0

    false_positives = flagged_users.intersection(legitimate_users)

    return len(false_positives) / len(legitimate_users)
