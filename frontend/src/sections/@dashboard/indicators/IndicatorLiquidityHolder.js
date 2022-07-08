// @mui
import PropTypes from 'prop-types';
import {
    Card,
    Grid,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Typography
} from '@mui/material';
import {createWalletAddressURL} from '../../../helperFunction';


IndicatorLiquidityHolder.propTypes = {
    color: PropTypes.string,
    sx: PropTypes.object,
    holderCount: PropTypes.number.isRequired,
    holdersObject: PropTypes.object.isRequired,
};


export default function IndicatorLiquidityHolder({
                                                     holderCount,
                                                     holdersObject,
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
                <Typography variant="h3">Liquidity Pool Holders</Typography>

                <Typography variant="body1" sx={{lineHeight: 2}}>
                    <b>Maximal Transaction Amount in ETH:</b> {holderCount ? holderCount : "No Holders available"} <br/>

                    <TableContainer component={Paper}>
                        <Table sx={{minWidth: 650}} aria-label="simple table">
                            <TableHead>
                                <TableRow>
                                    <TableCell>Share</TableCell>
                                    <TableCell align="left">Balance</TableCell>
                                    <TableCell align="left">Address</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {holdersObject !== null && holdersObject.map((holderObject) => (
                                    <TableRow
                                        key={holderObject.address ? holderObject.address : "0"}
                                        sx={{'&:last-child td, &:last-child th': {border: 0}}}
                                    >
                                        <TableCell component="th" scope="row">
                                            {holderObject.share ? holderObject.share : "0" } %
                                        </TableCell>
                                        <TableCell align="left">{holderObject.balance ? holderObject.balance : "Not Available"}</TableCell>
                                        <TableCell align="left">
                                            {createWalletAddressURL(holderObject.address ? holderObject.address : "Not Available")}
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </Typography>
            </Card>
        </Grid>
    );

}
