import React, {useEffect, useState} from "react";
import {useParams} from "react-router-dom";
// @mui
import {Button, Container, Grid, Typography} from '@mui/material';
// components
import Page from '../components/Page';
// sections
import GeneralInformation from "../sections/@dashboard/app/GeneralInformation";
import {unixTimeStampToDateTime} from "../helperFunction";
import IndicatorHoneypot from "../sections/@dashboard/indicators/IndicatorHoneypot";
import IndicatorTokenHolders from "../sections/@dashboard/indicators/IndicatorTokenHolders";
import ScoreGraph from "../sections/@dashboard/app/ScoreGraph";
import IndicatorSlither from "../sections/@dashboard/indicators/IndicatorSlither";
import IndicatorVerifiedContract from "../sections/@dashboard/indicators/IndicatorVerifiedContract";
import IndicatorLiquidityAmount from "../sections/@dashboard/indicators/IndicatorLiquidityAmount";
import IndicatorLiquidityHolder from "../sections/@dashboard/indicators/IndicatorLiquidityHolder";
import HeaderBasicOverview from "../sections/@dashboard/app/HeaderBasicOverview";
import Iconify from "../components/Iconify";
import AnalysisScanHistory from "../sections/@dashboard/indicators/AnalysisScanHistory";


// ----------------------------------------------------------------------

// ----------------------------------------------------------------------

export default function TokenDetail(props) {


// API call

    const [Token, setToken] = useState();
    const [TokenHistory, setTokenHistory] = useState();
    const {id} = useParams()

    const loadTokenDetail = async () => {
        try {
            let json

            const responseSubmission = await fetch(`${process.env.REACT_APP_BACKEND_URL_WITH_PORT}/getTokenFromSubmission/${id}`)

            if (responseSubmission.status !== 200) {
                const responseMonitor = await fetch(`${process.env.REACT_APP_BACKEND_URL_WITH_PORT}/getTokenFromMonitor/${id}`)

                if (responseMonitor.status !== 200) {
                    const responseAnalyzer = await fetch(`${process.env.REACT_APP_BACKEND_URL_WITH_PORT}/analyse/${id}`)
                    console.log(responseAnalyzer, 'responseAnalyzer')
                    if (responseAnalyzer.status !== 200) {
                        console.log('No token found')
                        let url = window.location.origin;
                        url += `/dashboard/token-list/`
                        window.location = url;
                    } else {
                        json = await responseAnalyzer.json()
                    }
                } else {
                    json = await responseMonitor.json()

                }
            } else {
                json = await responseSubmission.json()
            }

            setToken(json)
        } catch (error) {
            console.log(error)
        }


    }
    const getTokenHistory = async () => {
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL_WITH_PORT}/getScanHistory/${id}`)
            const json = await response.json()
            setTokenHistory(json)
        } catch (error) {
            console.log(error)
        }
    }

    const rescanToken = async () => {
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL_WITH_PORT}/analyse/${id}`)
            const json = await response.json()
            setToken(json)
            await getTokenHistory()
        } catch (error) {
            console.log(error)
        }
    }

    useEffect(() => {
        loadTokenDetail()
        getTokenHistory()
    }, [])

    if (!Token) return <></>


    return (<Page title="Token Details">
        <Container maxWidth="xl">
            <Typography variant="h4" sx={{mb: 5}}>
                Analysis {Token.name} {Token.symbol}
            </Typography>
            <Grid container
                  direction="row"
                  justifyContent="space-between"
                  alignItems="center">

                <Grid item xs={12} sm={6} md={6} sx={{mb: 5, marginBottom: 10}}>
                    <Typography variant="subtitle1" sx={{textAlign: "left"}}>
                        <p>Last scanned {unixTimeStampToDateTime(Token.scan_time)} UTC</p>
                    </Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={6} sx={{textAlign: "right"}}>
                    <Button variant="contained" startIcon={<Iconify icon="ant-design:redo-outlined"/>}
                            onClick={rescanToken}>
                        Rescan
                    </Button>
                </Grid>
            </Grid>

            <Grid container spacing={3}>
                <HeaderBasicOverview
                    ethLiquidity={Token?.liquidity_amount?.eth_liquidity}
                    holdersCount={Token?.holders?.holdersCount}
                    scamProbability={Token?.xgboost_scam_probability}
                    amountOfVulnerabilities={Token?.verified_contract?.slither_results.vulnerabilities.length}
                />


                <GeneralInformation
                    name={Token?.name}
                    address={Token?.address}
                    symbol={Token?.symbol}
                    humanSupply={Token?.human_supply}
                    creator={Token?.creator}
                    creationTime={Token?.creation_time}
                    creationBlock={Token?.creation_block}
                    creationTxHash={Token?.creation_tx_hash}
                    owner={Token?.owner}
                    transfersCount={Token?.transfers_count}
                />


                <IndicatorTokenHolders
                    holdersCount={Token?.holders?.holdersCount}
                    holdersObject={Token?.holders?.holders}
                />


                <IndicatorLiquidityAmount
                    ethLiquidity={Token?.liquidity_amount?.eth_liquidity}
                    lpAddress={Token?.liquidity_amount?.lp_address}
                />


                <IndicatorLiquidityHolder
                    lpAddress={Token?.liquidity_holders?.pair}
                    holderCount={Token?.liquidity_holders?.holdersCount}
                    holdersObject={Token?.liquidity_holders?.holders}
                />


                <IndicatorHoneypot
                    isHoneypot={Token?.honeypot?.IsHoneypot}
                    honeypotMessage={Token?.honeypot?.Error}
                    maxTxAmount={Token?.honeypot?.MaxTxAmount}
                    maxTxAmountEth={Token?.honeypot?.MaxTxAmountETH}
                    buyTax={Token?.honeypot?.BuyTax}
                    sellTax={Token?.honeypot?.SellTax}
                    buyGas={Token?.honeypot?.BuyGas}
                    sellGas={Token?.honeypot?.SellGas}
                />

                {/* Minor FE Bug, could not implement it into the Component */}
                <Grid item xs={12} md={12} lg={12}>
                    <IndicatorVerifiedContract
                        verifiedContractObject={Token?.verified_contract}
                    /></Grid>


                <IndicatorSlither
                    vulnerabilitiesObject={Token?.verified_contract?.slither_results?.vulnerabilities}
                />


                <ScoreGraph
                    resultObject={Token?.indicator_results}
                    customProbability={Token?.custom_scam_probability}
                    supportVectoreMachineProbablility={Token?.svm_scam_probability}
                    xgboostProbablility={Token?.xgboost_scam_probability}
                />

                    <AnalysisScanHistory
                    historyObject={TokenHistory}
                />


            </Grid>
        </Container>
    </Page>);
}
