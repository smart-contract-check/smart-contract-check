import indicators.general_information
import indicators.verified_contract
import indicators.honeypot_is
import indicators.liquidity
import indicators.liquidity_holders
import indicators.holders
import indicators.slither
import time


def collect_token_details(token):

    general_information = indicators.general_information.general_information(token)
    honeypot_result = indicators.honeypot_is.honeypot_is(token)
    liquidity_result = indicators.liquidity.get_liquidity(token)
    holders_result = indicators.holders.get_holders(token)
    liquidity_holders_result = indicators.liquidity_holders.get_liquidity_holders(token)
    verified_contract = indicators.verified_contract.process_verified_contract(token)

    scanned_time = time.time()

    general_information['honeypot'] = honeypot_result
    general_information['holders'] = holders_result
    general_information['liquidity_amount'] = liquidity_result
    general_information['liquidity_holders'] = liquidity_holders_result
    general_information['verified_contract'] = verified_contract
    general_information['scan_time'] = scanned_time

    return general_information
