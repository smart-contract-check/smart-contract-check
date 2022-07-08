def score_holder_share(share):
    if share > 98:
        return 0.81
    if share > 71:
        return 0.73
    if share > 61.0:
        return 0.676
    if share < 5:
        return 0.5
    else:
        return 0.5


def score_liquidity_share(share):
    if share is None:
        return 0.5
    if share == 0.0:
        return 0.75
    if share > 99.0:
        return 0.75
    if share > 80:
        return 0.6
    if share > 40:
        return 0.25
    if share < 5.0:
        return 0.5
    else:
        return 0.0


def score_liquidity_amount(amount):
    if amount is None:
        return 0.5
    if amount <= 0.002:
        return 1.0
    if amount <= 0.15:
        return 0.9
    if amount <= 0.5:
        return 0.8
    if amount <= 1.5:
        return 0.5
    if amount > 40:
        return 0.25
    else:
        return 0.5


def score_vulnerabilities(impact, confidence):

    if impact is None:
        return 0.5
    elif impact == 3 and confidence == 3:
        return 1.0
    else:
        return 0.5


def get_combined_score(result):
    scam_score = 0

    # importance_values = {
    #     "liquidity_share_confidence": 2,
    #     "holder_share_importance": 2,
    #     "liquidity_amount_importance": 2,
    #     "honeypot_importance": 3,
    #     "ownership_importance": 0,
    #     "verified_contract_importance": 5,
    #     "vulnerabilities_importance": 0.1,
    # }
    importance_values = {
        "liquidity_share_importance": 1,
        "holder_share_importance": 2,
        "liquidity_amount_importance": 2,
        "honeypot_importance": 2,
        "ownership_importance": 2,
        "verified_contract_importance": 2,
        "vulnerabilities_importance": 1,
    }

    if result['liquidity_share_result'] is None:
        scam_score += 0.5 * importance_values["liquidity_share_importance"]
    else:
        scam_score += result['liquidity_share_result'] * importance_values["liquidity_share_importance"]

    if result['holder_share_result'] is None:
        scam_score += 0.5 * importance_values["holder_share_importance"]
    else:
        scam_score += result['holder_share_result'] * importance_values["holder_share_importance"]

    if result['ownership_result'] is None:
        scam_score += 0.5 * importance_values["ownership_importance"]
    else:
        scam_score += result['ownership_result'] * importance_values["ownership_importance"]

    scam_score += result['liquidity_amount_result'] * importance_values["liquidity_amount_importance"]
    scam_score += result['honeypot_result'] * importance_values["honeypot_importance"]

    scam_score += result['verified_contract_result'] * importance_values["verified_contract_importance"]

    if result['vulnerabilities_result'] is None:
        scam_score += 0.5 * importance_values["vulnerabilities_importance"]
    else:
        scam_score += result['vulnerabilities_result'] * importance_values["vulnerabilities_importance"]

    avg_confidence = sum(importance_values.values())
    return scam_score / avg_confidence


DEFAULT_CONFIG = {
    "score_liquidity_share": score_liquidity_share,
    "score_holder_share": score_holder_share,
    "score_liquidity_amount": score_liquidity_amount,
    "score_vulnerabilities": score_vulnerabilities,
    "get_combined_score": get_combined_score
}
