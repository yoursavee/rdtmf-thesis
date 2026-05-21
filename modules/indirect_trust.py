import numpy as np
import pandas as pd
import networkx as nx
from collections import deque

from modules.direct_trust import combined_similarity


def build_trust_graph(rating_matrix, edge_threshold=0.50, min_corated=3):
    """
    Build a similarity-based user trust graph.

    Each user is a node.
    An edge is created between two users if their combined similarity
    is equal to or above the edge threshold.
    """
    graph = nx.Graph()

    total_users = rating_matrix.shape[0]

    # Add all users as graph nodes
    for user_id in range(total_users):
        graph.add_node(user_id)

    # Compare user pairs
    for i in range(total_users):
        user_i = rating_matrix.iloc[i]

        for j in range(i + 1, total_users):
            user_j = rating_matrix.iloc[j]

            common = user_i.notna() & user_j.notna()

            if common.sum() < min_corated:
                continue

            similarity = combined_similarity(
                user_i,
                user_j,
                min_corated=min_corated
            )

            if similarity >= edge_threshold:
                graph.add_edge(i, j, weight=similarity)

    return graph


def compute_indirect_trust(
    rating_matrix,
    graph,
    target_user,
    service_id,
    dmax=3,
    decay=0.7,
    edge_threshold=0.50,
    flagged_users=None
):
    """
    Compute Indirect Trust IT(u, s) using BFS and depth decay.

    The method explores reachable trusted users through the graph.
    Users farther away have lower influence because of depth decay.
    """
    if flagged_users is None:
        flagged_users = set()

    if target_user in flagged_users:
        return 0.0

    visited = set()
    queue = deque()

    # queue item: current_user, depth, path_trust
    queue.append((target_user, 0, 1.0))
    visited.add(target_user)

    contributions = []

    while queue:
        current_user, depth, path_trust = queue.popleft()

        if depth >= dmax:
            continue

        for neighbour in graph.neighbors(current_user):
            if neighbour in visited:
                continue

            if neighbour in flagged_users:
                continue

            edge_weight = graph[current_user][neighbour].get("weight", 0.0)

            if edge_weight < edge_threshold:
                continue

            new_depth = depth + 1

            # Path trust decreases as depth increases
            decayed_path_trust = path_trust * edge_weight * (decay ** new_depth)

            # If reachable neighbour has rated the target service,
            # use it as an indirect trust contribution.
            rating = rating_matrix.iloc[neighbour, service_id]

            if pd.notna(rating):
                contributions.append((decayed_path_trust, rating))

            visited.add(neighbour)
            queue.append((neighbour, new_depth, decayed_path_trust))

    if len(contributions) == 0:
        return 0.0

    numerator = sum(weight * rating for weight, rating in contributions)
    denominator = sum(abs(weight) for weight, rating in contributions)

    if denominator == 0:
        return 0.0

    indirect_trust = numerator / denominator

    return float(np.clip(indirect_trust, 0, 1))
