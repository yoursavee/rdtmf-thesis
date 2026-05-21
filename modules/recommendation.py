import pandas as pd


def generate_top_n_recommendations(
    final_trust_df,
    target_user,
    n=5,
    trust_threshold=0.60,
    flagged_users=None
):
    """
    Generate Top N trusted service recommendations for a target user.

    Only services with final_trust >= trust_threshold are recommended.
    If the target user is flagged as malicious or low-trust, no recommendation is returned.
    """

    if flagged_users is None:
        flagged_users = set()

    if target_user in flagged_users:
        return pd.DataFrame(columns=[
            "user_id",
            "service_id",
            "final_trust",
            "recommendation_rank",
            "status"
        ])

    user_services = final_trust_df[
        final_trust_df["user_id"] == target_user
    ].copy()

    trusted_services = user_services[
        user_services["final_trust"] >= trust_threshold
    ].copy()

    trusted_services = trusted_services.sort_values(
        by="final_trust",
        ascending=False
    )

    top_n = trusted_services.head(n).copy()

    top_n["recommendation_rank"] = range(1, len(top_n) + 1)
    top_n["status"] = "Recommended"

    return top_n[
        [
            "user_id",
            "service_id",
            "direct_trust",
            "indirect_trust",
            "final_trust",
            "recommendation_rank",
            "status"
        ]
    ]
