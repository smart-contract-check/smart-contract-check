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
import {fShortenNumber} from "../../../utils/formatNumber";
import {unixTimeStampToDateTime} from "../../../helperFunction";


AnalysisScanHistory.propTypes = {
    color: PropTypes.string,
    sx: PropTypes.object,
    holdersObject: PropTypes.object,

};

export default function AnalysisScanHistory({
                                                historyObject,
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
                <Typography variant="h3">Scan History</Typography>

                <Typography variant="body1" sx={{lineHeight: 2}}>
                    <TableContainer component={Paper}>
                        <Table sx={{minWidth: 650}} aria-label="simple table">
                            <TableHead>
                                <TableRow>
                                    <TableCell>Scan Time (UTC)</TableCell>
                                    <TableCell align="left">Liquidity Amount</TableCell>
                                    <TableCell align="left">Custom Score</TableCell>
                                    <TableCell align="left">SVM Score</TableCell>
                                    <TableCell align="left">XGBoost Score</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {historyObject.map(({scan_time, custom_scam_probability, svm_scam_probability, xgboost_scam_probability, liquidity_amount}) => (
                                    <TableRow
                                        key={scan_time}
                                        sx={{'&:last-child td, &:last-child th': {border: 0}}}
                                    >
                                        <TableCell component="th" scope="row">
                                            {unixTimeStampToDateTime(scan_time)}
                                        </TableCell>
                                        <TableCell>
                                            {liquidity_amount ? liquidity_amount : "Not Pair with"} WETH
                                        </TableCell>
                                        <TableCell>
                                            {fShortenNumber(custom_scam_probability * 100)}%
                                        </TableCell>
                                        <TableCell
                                            align="left">{fShortenNumber(svm_scam_probability * 100)}%</TableCell>
                                        <TableCell align="left">
                                            {fShortenNumber(xgboost_scam_probability * 100)}%
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
