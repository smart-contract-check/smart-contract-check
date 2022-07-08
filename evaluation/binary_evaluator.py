import evaluation.wallet_constant


def get_score(evaluate_coin, percentage_considered_whale, liquidity_eth_considered_scam, set_weights):
    top_holders = evaluate_coin["holders"]["holders"]
    is_top_holder_score = evaluate_top_holders(top_holders, percentage_considered_whale)

    verified_contract = evaluate_coin["verified_contract"]
    is_verified_contract_score = evaluate_verified_contract(verified_contract)

    honeypot_result = evaluate_coin["honeypot"]
    is_honeypot_score = evaluate_honeypot(honeypot_result)

    liquidity_pool_amount = evaluate_coin["liquidity_amount"]
    is_liquidity_pool_amount_score = evaluate_liquidity(liquidity_pool_amount, liquidity_eth_considered_scam)

    total_weight = sum(set_weights.values())

    end_score = (is_top_holder_score * set_weights["top_holder_weight"]
                 + is_verified_contract_score * set_weights["verified_contract_weight"]
                 + is_honeypot_score * set_weights["honeypot_score_weight"]
                 + is_liquidity_pool_amount_score * set_weights["liquidity_pool_amount_weight"]
                 ) / total_weight

    result_set = {
        "top_holder_score": is_top_holder_score,
        "verified_contract_score": is_verified_contract_score,
        "honeypot_score": is_honeypot_score,
        "liquidity_pool_amount_score": is_liquidity_pool_amount_score,
        "end_score": end_score,
        "weight_per_indicator": set_weights,
    }

    return result_set


# Burning Address --> In Backend
def check_is_burning_address(input_address):
    is_burning_address = False
    for address in evaluation.wallet_constant.BURNING_ADDRESSES:
        # Since there are different writing styles of the HEX Code, need to lower the address
        if address.lower() == input_address.lower():
            is_burning_address = True

        return is_burning_address


def burning_address_evaluate(top_holders):
    is_top_holder_burning_address = 0

    for address in top_holders:
        is_burning_address = check_is_burning_address(address)
        if is_burning_address == 1:
            is_top_holder_burning_address = 1

    return is_top_holder_burning_address


def evaluate_verified_contract(verified_contract_information):
    compiler_version = verified_contract_information["SourceCode"]
    is_verified = 0

    if compiler_version != "":
        is_verified = 1
    return is_verified


def evaluate_honeypot(honeypot_result):
    return int(honeypot_result["IsHoneypot"])


def evaluate_liquidity(liquidity_result, liquidity_eth_considered_scam):
    liquidity_reserve_eth = float(liquidity_result["eth_liquidity"])
    is_low_liquidity = 0
    if liquidity_reserve_eth >= liquidity_eth_considered_scam:
        is_low_liquidity = 1

    return is_low_liquidity


def evaluate_top_holders(top_holders, percentage_considered_whale):
    if top_holders[0]["share"] < percentage_considered_whale:
        return 1

    return 0
