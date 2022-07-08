import evaluation.wallet_constant


def get_score(evaluate_coin, liquidity_eth_considered_scam):
    trust_score_sum = 0
    indicator_count = 4

    top_holders = evaluate_coin["holders"]["holders"]
    top_holder_score = evaluate_top_holders(top_holders)
    trust_score_sum += top_holder_score

    verified_contract = evaluate_coin["verified_contract"]
    verified_contract_score = evaluate_verified_contract(verified_contract)
    trust_score_sum += verified_contract_score

    honeypot_result = evaluate_coin["honeypot"]
    honeypot_score = evaluate_honeypot(honeypot_result)
    trust_score_sum += honeypot_score

    liquidity_result = evaluate_coin["liquidity_amount"]
    liquidity_pool_amount_score = evaluate_liquidity(liquidity_result, 1, 10)
    trust_score_sum += liquidity_pool_amount_score

    end_score = trust_score_sum / indicator_count

    result_set = {
        "top_holder_score": top_holder_score,
        "verified_contract_score": verified_contract_score,
        "honeypot_score": honeypot_score,
        "liquidity_pool_amount_score": liquidity_pool_amount_score,
        "end_score": end_score
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
    is_top_holder_burning_address = False

    for address in top_holders:
        is_burning_address = check_is_burning_address(address)
        if not is_burning_address:
            is_top_holder_burning_address = True

    return is_top_holder_burning_address


def evaluate_verified_contract(verified_contract_information):
    compiler_version = verified_contract_information["CompilerVersion"]
    is_verified = 0.2

    if compiler_version != "":
        is_verified = 0.8
    return is_verified


def evaluate_honeypot(honeypot_result):
    is_honeypot = honeypot_result["IsHoneypot"]
    score = 0.2

    if not is_honeypot:
        score = 0.9

    return score


def evaluate_liquidity(liquidity_result, liquidity_min, liquidity_max):
    liquidity_reserve_eth = float(liquidity_result["eth_liquidity"])
    score = 0
    # Everything between min and max are distributed from 0 to 1
    if liquidity_reserve_eth <= liquidity_min:
        score = 0
    elif liquidity_reserve_eth > liquidity_max:
        score = 1
    else:
        score = (liquidity_reserve_eth - liquidity_min) / (liquidity_max - liquidity_min)

    return score


def evaluate_top_holders(top_holders):
    score = 0
    for address in top_holders:
        if not check_is_burning_address(address["address"]):
            # Percentage change under 50% is linear between 0 and 1 from 50% on is considered a scam
            if address["share"] < 50:
                score = 1 - (address["share"] / 100 * 2)
            else:
                score = 0
            break

    return score
