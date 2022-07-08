import logging
from web3 import Web3
from evaluation.wallet_constant import BURNING_ADDRESSES
from evaluation.wallet_constant import LIQUIDITY_LOCKERS
from monitor.known_addresses import KNOWN_ADDRESSES
from scipy.stats import norm
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
from sklearn.svm import SVC
import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler
import xgboost as xgb

SUSPICIOUS_VULNERABILITIES = {
    "array-by-reference": 1,
    "incorrect-shift": 1,
    "multiple-constructors": 1,
    "name-reused": 1,
    "public-mappings-nested": 1,
    "rtlo": 1,
    "shadowing-state": 1,
    "suicidal": 1,
    "uninitialized-state": 1,
    "uninitialized-storage": 1,
    "unprotected-upgrade": 1,
    "arbitrary-send": 1,
    "reentrancy-eth": 1,
    "incorrect-equality": 1,
    "locked-ether": 1,
    "shadowing-abstract": 0.75,
    "write-after-write": 1,
    "boolean-cst": 1,
    "divide-before-multiply": 0.75,
    "reentrancy-no-eth": 0.75,
    "tx-origin": 1,
    "unchecked-lowlevel": 1,
    "unused-return": 0.75,
    "shadowing-local": 1,
    "events-maths": 0.75,
}


class Evaluator:

    def __init__(self, token, config):
        self.token = token
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.custom_classifier = joblib.load('evaluation/svc_linear_classifier.joblib')
        self.custom_scaler = joblib.load('evaluation/custom_data_scaler.joblib')
        self.svm_classifier = joblib.load('evaluation/svc_rbf_classifier.joblib')
        self.svm_scaler = joblib.load('evaluation/svm_data_scaler.joblib')
        self.xgboost_classifier = joblib.load('evaluation/xgb_classifier.joblib')
        self.xgboost_scaler = joblib.load('evaluation/xgb_data_scaler.joblib')
        self.result, self.total_score = self._calculate_score()

    def get_highest_token_holder_share(self):
        circulating_supply = float(self.token['supply'])
        token_holders = self.token['holders']['holders']

        highest_share = None
        lp_address = self.token['liquidity_holders']['pair'].lower()
        for holder in token_holders:
            holder_address = holder['address'].lower()
            if holder_address in BURNING_ADDRESSES:
                circulating_supply -= float(holder['balance'])

        for holder in token_holders:
            holder_address = holder['address'].lower()
            if holder_address == lp_address or holder_address in BURNING_ADDRESSES:
                continue
            else:
                share = 100.0 / circulating_supply * float(holder['balance'])
                highest_share = share
                break

        return highest_share

    def get_highest_liquidity_holder_share(self):

        if self.token['liquidity_holders'] is None:
            return None

        liquidity_holders = self.token['liquidity_holders']['holders']

        if liquidity_holders is None:
            return None

        highest_liquidity_holder = 0
        # not sure, this just makes semantically sense. If holders exist but all are locked / burned
        # it is basically 0 share. However this did hit mostly scams for whatever reason

        for holder in liquidity_holders:
            if holder['address'].lower() in LIQUIDITY_LOCKERS or holder['address'].lower() in BURNING_ADDRESSES or holder['address'].lower() in KNOWN_ADDRESSES:
                continue
            else:
                highest_liquidity_holder = holder['share']
                break

        return highest_liquidity_holder

    def get_renounced_ownership(self):
        if self.token['owner'].lower() == "0x":
            return None
        if self.token['owner'].lower() in BURNING_ADDRESSES:
            return 0.0
        else:
            return 0.5

    def get_eth_liquidity(self):
        if self.token['liquidity_amount']['eth_liquidity'] is None:
            return None
        else:
            return float(self.token['liquidity_amount']['eth_liquidity'])

    def get_verified_contract(self):
        if self.token['verified_contract']['SourceCode'] == "":
            return False
        else:
            return True

    def get_highest_vulnerability(self):  # returns impact, confidence
        slither_results = self.token['verified_contract']['slither_results']
        if self.token['verified_contract']['SourceCode'] == "":
            return 0.5, 0.5

        if slither_results['error'] == 2:
            return 0.5, 0.5

        if slither_results['error'] == 1:
            return 0.5, 0.5

        if not slither_results['vulnerabilities']:
            return 0.0, 0.0

        else:
            severities = {
                "High": 3,
                "Medium": 2,
                "Low": 1,
            }
            # highest_vulnerability = slither_results['vulnerabilities'][0]
            # return severities[highest_vulnerability['impact']], severities[highest_vulnerability['confidence']]

            highest_vulnerability = [0, 0]
            for vuln in slither_results['vulnerabilities']:
                new_impact = severities[vuln['impact']]
                new_confidence = severities[vuln['confidence']]
                if (new_impact + new_confidence) > (highest_vulnerability[0] + highest_vulnerability[1]):
                    highest_vulnerability = [new_impact, new_confidence]
            return highest_vulnerability[0], highest_vulnerability[1]

        # for vuln in slither_results['vulnerabilities']:
        #     if vuln['impact'] in ["High", "Medium"] and vuln['confidence'] in ["Medium", "High"]:
        #         if vuln['impact'] == "High" and vuln['impact'] == "High":
        #             found_high = True

    def _evaluate_renounced_ownership(self):
        revoked_ownership = self.get_renounced_ownership()
        if revoked_ownership is None:
            return 0.75
        if revoked_ownership == 0.0:
            return 0.75
        else:
            return 0.5

    def _evaluate_honeypot(self):

        if self.token['honeypot']['IsHoneypot']:
            return 1.0
        else:
            return 0.5

    def _evaluate_liquidity(self):
        eth_liquidity = self.get_eth_liquidity()
        return self.config['score_liquidity_amount'](eth_liquidity)

    def _evaluate_verified_contract(self):
        verified_contract = self.get_verified_contract()
        if verified_contract:
            return 0.5
        else:
            return 1.0

    def _evaluate_vulnerabilities(self):
        slither_results = self.token['verified_contract']['slither_results']

        if self.token['verified_contract']['SourceCode'] == "":
            return 0.5

        if slither_results['error'] == 2:
            return 1.0

        if slither_results['error'] == 1:
            return 0.5

        highest_vuln_score = 0.25
        for vuln in slither_results['vulnerabilities']:
            try:
                vuln_score = SUSPICIOUS_VULNERABILITIES[vuln['check']]
                if highest_vuln_score < vuln_score:
                    highest_vuln_score = vuln_score
            except:
                continue

        return highest_vuln_score
        # return self.config['score_vulnerabilities'](highest_vulnerability_impact, highest_vulnerability_confidence)

    def _evaluate_token_holders(self):
        share = self.get_highest_token_holder_share()
        if share is None:
            return 0.5
        elif share > 100:
            return 1.0
        else:
            return self.config['score_holder_share'](share)

    def _evaluate_liquidity_holders(self):

        share = self.get_highest_liquidity_holder_share()

        return self.config['score_liquidity_share'](share)

    def _calculate_score(self):
        liquidity_share_result = self._evaluate_liquidity_holders()
        holder_share_result = self._evaluate_token_holders()
        liquidity_amount_result = self._evaluate_liquidity()
        honeypot_result = self._evaluate_honeypot()
        ownership_result = self._evaluate_renounced_ownership()
        verified_contract_result = self._evaluate_verified_contract()
        vulnerabilities_result = self._evaluate_vulnerabilities()

        result = {
            "liquidity_share_result": liquidity_share_result,
            "holder_share_result": holder_share_result,
            "liquidity_amount_result": liquidity_amount_result,
            "honeypot_result": honeypot_result,
            "ownership_result": ownership_result,
            "verified_contract_result": verified_contract_result,
            "vulnerabilities_result": vulnerabilities_result
        }

        total_score = self.config['get_combined_score'](result)

        return result, total_score

    def get_score(self):
        return self.result, self.total_score

    def get_custom_scam_result(self):
        x = self.custom_scaler.transform(np.array(self.total_score).reshape(-1, 1))
        guess = self.custom_classifier.predict(x)
        probability = self.custom_classifier.predict_proba(x)

        return guess, probability

    def get_svm_scam_result(self):
        x = self.svm_scaler.transform(np.array([self.result['liquidity_share_result'],
                                                self.result['holder_share_result'],
                                                self.result['liquidity_amount_result'],
                                                self.result['honeypot_result'],
                                                self.result['ownership_result'],
                                                self.result['verified_contract_result'],
                                                self.result['vulnerabilities_result']]).reshape(-1, 7))

        guess = self.svm_classifier.predict(x)
        probability = self.svm_classifier.predict_proba(x)

        return guess, probability

    def get_xgb_scam_result(self):
        x = self.xgboost_scaler.transform(np.array([self.result['liquidity_share_result'],
                                                self.result['holder_share_result'],
                                                self.result['liquidity_amount_result'],
                                                self.result['honeypot_result'],
                                                self.result['ownership_result'],
                                                self.result['verified_contract_result'],
                                                self.result['vulnerabilities_result']]).reshape(-1, 7))

        x = xgb.DMatrix(x)
        probability = self.xgboost_classifier.predict(x)
        guess = [round(value) for value in probability]

        return guess, probability
