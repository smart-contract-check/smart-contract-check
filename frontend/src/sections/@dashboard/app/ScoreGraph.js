// @mui
import PropTypes from 'prop-types';
import {Card, Grid, Typography} from '@mui/material';
import {useTheme} from "@mui/material/styles";
import {AppCurrentSubject} from "./index";
import {fShortenNumber} from "../../../utils/formatNumber";


ScoreGraph.propTypes = {
    resultObject: PropTypes.object,
    endResult: PropTypes.number,
    color: PropTypes.string,
    sx: PropTypes.object,
};

// https://stackoverflow.com/questions/286141/remove-blank-attributes-from-an-object-in-javascript
function cleanObjectFromNull(obj) {
    return Object.entries(obj)
        .filter(([_, v]) => v != null)
        .reduce((acc, [k, v]) => ({...acc, [k]: v}), {});
}


function multiplyObjectValueBy100(obj) {
    return Object.entries(obj)
        .reduce((acc, [k, v]) => ({...acc, [k]: v * 100}), {});
}

// remove all "results" from keys and replace all _ with space and make first letter big
function replaceAllKeysAndFirstLetterBig(obj) {
    return Object.entries(obj)
        .reduce((acc, [k, v]) => ({
            ...acc,
            [k.replace(/result/g, '').replace(/_/g, ' ').replace(/^\w/, c => c.toUpperCase())]: v
        }), {});
}

export default function ScoreGraph({
                                       resultObject,
                                       customProbability,
                                       supportVectoreMachineProbablility,
                                       xgboostProbablility,
                                       color = 'background', sx, ...other
                                   }) {
    const theme = useTheme();
    const resultWithOutNull = replaceAllKeysAndFirstLetterBig(cleanObjectFromNull(resultObject))
    const labelArray = Object.keys(resultWithOutNull)
    const percentageResult = multiplyObjectValueBy100(resultWithOutNull)
    const dataArray = Object.values(percentageResult)
    const maxYValue = 100


    return (
        <Grid item xs={12} md={12} lg={12}>
            <Card
                sx={{
                    py: 5,
                    boxShadow: 0,
                    textAlign: 'left',
                    padding: 5,
                    color: (theme) => theme.palette[color].darker,
                    bgcolor: (theme) => theme.palette[color].lighter,
                    ...sx,
                }}
                {...other}
            >
                <Typography variant="h3">Final Score</Typography>

                <Typography variant="body1" sx={{lineHeight: 2}}>
                    <b>Custom Score:</b> {fShortenNumber(customProbability * 100)}% Scam<br/>
                    <b>Support Vector Machine:</b> {fShortenNumber(supportVectoreMachineProbablility * 100)}% Scam<br/>
                    <b>XGBoost:</b> {fShortenNumber(xgboostProbablility * 100)}% Scam<br/>

                    <AppCurrentSubject
                        title="Scores of the Indicators"

                        chartLabels={labelArray}
                        chartData={[
                            {name: 'Smart Contract', data: dataArray},
                        ]}
                        chartColors={[...Array(resultObject.length)].map(() => theme.palette.text.secondary)}
                        maxYValue={maxYValue}
                    />
                </Typography>
            </Card>
        </Grid>
    );

}
