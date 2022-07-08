// @mui
import PropTypes from 'prop-types';
import {Card, Grid, Typography} from '@mui/material';


IndicatorHoneypot.propTypes = {
    color: PropTypes.string,
    sx: PropTypes.object,
    isHoneypot: PropTypes.bool,
    honeypotMessage: PropTypes.string,
    maxTxAmount: PropTypes.string,
    maxTxAmountEth: PropTypes.string,
    buyTax: PropTypes.string,
    sellTax: PropTypes.string,
    buyGas: PropTypes.string,
    sellGas: PropTypes.string,
};


export default function IndicatorHoneypot({

                                              isHoneypot,
                                              honeypotMessage,
                                              maxTxAmount,
                                              maxTxAmountEth,
                                              buyTax,
                                              sellTax,
                                              buyGas,
                                              sellGas,
                                              color = 'background', sx, ...other
                                          }) {
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
                <Typography variant="h3">Honeypot Analysis from <a href="https://www.honeypot.is/ethereum"
                                                                   target="_blank"
                                                                   rel="noreferrer">Honeypot.is</a></Typography>

                <Typography variant="body1" sx={{lineHeight: 2}}>
                    <b>Is it a Honeypot:</b> {isHoneypot ? "Yes" : "No"} <br/>
                    <b>Message on Honeypot.is:</b> {honeypotMessage} <br/>
                    <b>Maximal Transaction Amount:</b> {maxTxAmount} <br/>
                    <b>Maximal Transaction Amount in ETH:</b> {maxTxAmountEth} <br/>
                    <b>Percentage fees on buy:</b> {buyTax}% <br/>
                    <b>Percentage fees on sells:</b> {sellTax}% <br/>
                    <b>Gas fees on buy:</b> {buyGas} <br/>
                    <b>Gas fees on sells:</b> {sellGas} <br/>
                </Typography>
            </Card>
        </Grid>
    );

}
