// @mui
import PropTypes from 'prop-types';
import {Card, Grid, Typography} from '@mui/material';
import {
    createTokenURL,
    createTransactionURL,
    createWalletAddressURL,
    unixTimeStampToDateTime
} from '../../../helperFunction';


GeneralInformation.propTypes = {
    color: PropTypes.string,
    sx: PropTypes.object,
    name: PropTypes.string,
    address: PropTypes.string,
    symbol: PropTypes.string,
    humanSupply: PropTypes.string,
    creator: PropTypes.string,
    creationTime: PropTypes.number,
    creationBlock: PropTypes.number,
    creationTxHash: PropTypes.string,
    owner: PropTypes.string,
    transfersCount: PropTypes.number,
};

export default function GeneralInformation({
                                               name,
                                               address,
                                               symbol,
                                               humanSupply,
                                               creator,
                                               creationTime,
                                               creationBlock,
                                               creationTxHash,
                                               owner,
                                               transfersCount,
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
                <Typography variant="h3">General Information</Typography>

                <Typography variant="body1" sx={{lineHeight: 2}}>
                    <b>Name:</b> {name} <br/>
                    <b>Symbol:</b> {symbol} <br/>
                    <b>Address:</b> {createWalletAddressURL(address)} <br/>
                    <b>Supply:</b> {humanSupply} <br/>
                    <b>Owner:</b> {owner === "0x" ? "No owner available" : createWalletAddressURL(owner)} <br/>
                    <b>Creator address:</b> {createTokenURL(creator)} <br/>
                    <b>Creation time:</b> {unixTimeStampToDateTime(creationTime)} UTC <br/>
                    <b>Creation block number:</b> {creationBlock} <br/>
                    <b>Creation transaction hash:</b> {createTransactionURL(creationTxHash)} <br/>
                    <b>Transfer count:</b> {transfersCount} <br/>
                </Typography>
            </Card>
        </Grid>
    );
}
