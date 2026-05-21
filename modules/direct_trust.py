import numpy as np
import pandas as pd


def pearson_similarity(user_a, user_b, min_corated=3):
    """
    Calculate Pearson Correlation Coefficient between two users
    using only co-rated services.
    """
    common = user_a.notna() & user_b.notna()

    if common.sum() < min_corated:
        return 0.0

    a = user_a[common].values
    b = user_b[common].values

    if np.std(a) == 0 or np.std(b) == 0:
        return 0.0

    score = np.corrcoef(a, b)[0, 1]

    if np.isnan(score):
        return 0.0

    return float(score)


def cosine_similarity(user_a, user_b, min_corated=3):
    """
    Calculate Cosine Similarity between two users
    using only co-rated services.
    """
    common = user_a.notna() & user_b.notna()

    if common.sum() < min_corated:
        return 0.0

    a = user_a[common].values
    b = user_b[common].values

    denominator = np.linalg.norm(a) * np.linalg.norm(b)

    if denominator == 0:
        return 0.0

    score = np.dot(a, b) / denominator

    if np.isnan(score):
        return 0.0

    return float(score)


def angle_of_inclination(similarity):
    """
    Convert similarity score into angle of inclination.
    """
    similarity = np.clip(similarity, -1, 1)
    angle = np.degrees(np.arccos(similarity))
    return float(angle)


def combined_similarity(user_a, user_b, min_corated=3, aoi_threshold=80):
    """
    Combine PCC and Cosine Similarity, then apply AOI filter.
    """
    pcc = pearson_similarity(user_a, user_b, min_corated=min_corated)
    cosine = cosine_similarity(user_a, user_b, min_corated=min_corated)

    similarity = (pcc + cosine) / 2

    if similarity <= 0:
        return 0.0

    angle = angle_of_inclination(similarity)

    if angle > aoi_threshold:
        return 0.0

    return float(similarity)


def get_top_k_neighbours(rating_matrix, target_user, service_id, k=10, min_corated=3):
    """
    Find Top K similar users who have rated the target service.
    """
    target_vector = rating_matrix.iloc[target_user]
    neighbours = []

    for other_user in rating_matrix.index:
        if other_user == target_user:
            continue

        other_vector = rating_matrix.iloc[other_user]

        # Neighbour must have rated the target service
        if pd.isna(rating_matrix.iloc[other_user, service_id]):
            continue

        common = target_vector.notna() & other_vector.notna()

        if common.sum() < min_corated:
            continue

        sim = combined_similarity(
            target_vector,
            other_vector,
            min_corated=min_corated
        )

        if sim > 0:
            neighbours.append((other_user, sim))

    neighbours = sorted(neighbours, key=lambda x: x[1], reverse=True)

    return neighbours[:k]


def compute_direct_trust(rating_matrix, target_user, service_id, k=10, min_corated=3):
    """
    Compute Direct Trust DT(u, s) using similarity-weighted ratings.
    """
    neighbours = get_top_k_neighbours(
        rating_matrix=rating_matrix,
        target_user=target_user,
        service_id=service_id,
        k=k,
        min_corated=min_corated
    )

    if len(neighbours) == 0:
        return 0.0

    numerator = 0.0
    denominator = 0.0

    for neighbour_id, similarity in neighbours:
        rating = rating_matrix.iloc[neighbour_id, service_id]

        if pd.notna(rating):
            numerator += similarity * rating
            denominator += abs(similarity)

    if denominator == 0:
        return 0.0

    direct_trust = numerator / denominator

    return float(np.clip(direct_trust, 0, 1))
