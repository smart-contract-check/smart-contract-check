// @mui
import PropTypes from 'prop-types';
import {Card, Grid, Typography} from '@mui/material';
import {createTokenURL} from '../../../helperFunction';


IndicatorLiquidityAmount.propTypes = {
    color: PropTypes.string,
    sx: PropTypes.object,
    ethLiquidity: PropTypes.string.isRequired,
    lpAddress: PropTypes.string.isRequired,
};


export default function IndicatorLiquidityAmount({
                                                     ethLiquidity,
                                                     lpAddress,
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
                <Typography variant="h3">Liquidity Pool Amount</Typography>

                <Typography variant="body1" sx={{lineHeight: 2}}>
                    <b>Liquidity in Liquidity Pool:</b> {ethLiquidity ? ethLiquidity : "No Pair with"} WETH<br/>
                    <b>Liquidity Pool Address:</b> {createTokenURL(lpAddress)} <br/>
                </Typography>
            </Card>
        </Grid>
    );

}
