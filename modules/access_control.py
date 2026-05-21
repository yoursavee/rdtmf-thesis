def check_rbac_permission(user_role, service_id, rbac_policy):
    """
    Check whether a user role is allowed to access a service.
    """

    allowed_services = rbac_policy.get(user_role, [])

    if "ALL" in allowed_services:
        return True

    if service_id in allowed_services:
        return True

    return False


def final_access_decision(
    user_id,
    user_role,
    service_id,
    final_trust_score,
    rbac_policy,
    trust_threshold=0.60,
    flagged_users=None
):
    """
    Make final access decision using:
    1. flagged-user status
    2. trust threshold
    3. RBAC role permission
    """

    if flagged_users is None:
        flagged_users = set()

    if user_id in flagged_users:
        return {
            "user_id": user_id,
            "service_id": service_id,
            "user_role": user_role,
            "final_trust_score": final_trust_score,
            "access_decision": "Access Denied",
            "reason": "User is flagged as malicious or low-trust"
        }

    if final_trust_score < trust_threshold:
        return {
            "user_id": user_id,
            "service_id": service_id,
            "user_role": user_role,
            "final_trust_score": final_trust_score,
            "access_decision": "Access Denied",
            "reason": "Final trust score below threshold"
        }

    has_permission = check_rbac_permission(
        user_role=user_role,
        service_id=service_id,
        rbac_policy=rbac_policy
    )

    if has_permission:
        return {
            "user_id": user_id,
            "service_id": service_id,
            "user_role": user_role,
            "final_trust_score": final_trust_score,
            "access_decision": "Access Granted",
            "reason": "Trusted recommendation and valid RBAC permission"
        }

    return {
        "user_id": user_id,
        "service_id": service_id,
        "user_role": user_role,
        "final_trust_score": final_trust_score,
        "access_decision": "Access Denied",
        "reason": "Role-policy mismatch"
    }
