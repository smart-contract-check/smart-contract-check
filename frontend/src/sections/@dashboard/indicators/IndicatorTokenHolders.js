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


IndicatorTokenHolders.propTypes = {
    color: PropTypes.string,
    sx: PropTypes.object,
    holdersCount: PropTypes.number,
    holders: PropTypes.object,

};


export default function IndicatorTokenHolders({

                                                  holdersCount,
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
                <Typography variant="h3">Token Holder</Typography>

                <Typography variant="body1" sx={{lineHeight: 2}}>
                    <b>Amount Token Holders:</b> {holdersCount} <br/>
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
                                {holdersObject.map((holder) => (
                                    <TableRow
                                        key={holder.name}
                                        sx={{'&:last-child td, &:last-child th': {border: 0}}}
                                    >
                                        <TableCell component="th" scope="row">
                                            {holder.share} %
                                        </TableCell>
                                        <TableCell align="left">{holder.balance}</TableCell>
                                        <TableCell align="left">
                                            {createWalletAddressURL(holder.address)}
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
