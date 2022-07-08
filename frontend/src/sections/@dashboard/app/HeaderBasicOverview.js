// @mui
import PropTypes from 'prop-types';
import {Grid,} from '@mui/material';
import {AppWidgetSummary} from "./index";
import {fShortenNumber} from "../../../utils/formatNumber";


HeaderBasicOverview.propTypes = {
    color: PropTypes.string,
    sx: PropTypes.object,
    ethLiquidity: PropTypes.string.isRequired,
    holdersCount: PropTypes.number.isRequired,
    scamProbability: PropTypes.number.isRequired,
    amountOfVulnerabilities: PropTypes.number.isRequired,
};


export default function HeaderBasicOverview({
                                                ethLiquidity,
                                                holdersCount,
                                                scamProbability,
                                                amountOfVulnerabilities = "Not Available",
                                                color = 'background', sx, ...other
                                            }) {
    return (

        <>
            <Grid item xs={12} sm={6} md={3}>
                <AppWidgetSummary title="Total in Liquidity Pool"
                                  total={fShortenNumber(parseFloat(ethLiquidity))}
                                  suffix={" WETH"} icon={'ant-design:dollar-circle-outlined'}/>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
                <AppWidgetSummary title="Amount Token holders" total={holdersCount} color="info"
                                  icon={'ant-design:team-outlined'}/>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
                <AppWidgetSummary title="Percentage Scam on XGBoost" total={scamProbability * 100} suffix={"%"}
                                  color="warning" icon={'ant-design:search-outlined'}/>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
                <AppWidgetSummary title="Slither Vulnerabilities"
                                  total={amountOfVulnerabilities} color="error"
                                  icon={'ant-design:bug-filled'}/>
            </Grid>
        </>
    );

}
