import numpy as np
import pandas as pd


def calculate_mae(y_true, y_pred):
    y_true = np.array(y_true, dtype=float)
    y_pred = np.array(y_pred, dtype=float)

    valid = ~np.isnan(y_true) & ~np.isnan(y_pred)

    if valid.sum() == 0:
        return None

    return float(np.mean(np.abs(y_true[valid] - y_pred[valid])))


def calculate_rmse(y_true, y_pred):
    y_true = np.array(y_true, dtype=float)
    y_pred = np.array(y_pred, dtype=float)

    valid = ~np.isnan(y_true) & ~np.isnan(y_pred)

    if valid.sum() == 0:
        return None

    return float(np.sqrt(np.mean((y_true[valid] - y_pred[valid]) ** 2)))


def calculate_coverage(prediction_df, score_column="final_trust"):
    total_rows = len(prediction_df)

    if total_rows == 0:
        return 0.0

    predicted_rows = prediction_df[score_column].notna().sum()

    return float(predicted_rows / total_rows)


def calculate_precision_at_n(recommendations_df, actual_quality_df, target_user, relevance_threshold=0.60):
    if len(recommendations_df) == 0:
        return 0.0

    relevant_count = 0

    for _, row in recommendations_df.iterrows():
        service_id = int(row["service_id"])

        actual_score = actual_quality_df.iloc[target_user, service_id]

        if pd.notna(actual_score) and actual_score >= relevance_threshold:
            relevant_count += 1

    return float(relevant_count / len(recommendations_df))


def calculate_recall_at_n(recommendations_df, actual_quality_df, candidate_services, target_user, relevance_threshold=0.60):
    relevant_services = []

    for service_id in candidate_services:
        actual_score = actual_quality_df.iloc[target_user, int(service_id)]

        if pd.notna(actual_score) and actual_score >= relevance_threshold:
            relevant_services.append(service_id)

    if len(relevant_services) == 0:
        return 0.0

    recommended_services = set(recommendations_df["service_id"].astype(int).tolist())
    relevant_services = set(map(int, relevant_services))

    retrieved_relevant = recommended_services.intersection(relevant_services)

    return float(len(retrieved_relevant) / len(relevant_services))


def calculate_access_decision_consistency(access_df):
    if len(access_df) == 0:
        return 0.0

    valid_decisions = access_df["access_decision"].isin(["Access Granted", "Access Denied"])

    return float(valid_decisions.mean())
