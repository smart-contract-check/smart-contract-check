// @mui
import PropTypes from 'prop-types';
import {Accordion, AccordionDetails, AccordionSummary, Card, Grid, Typography} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import {Prism as SyntaxHighlighter} from 'react-syntax-highlighter';
import {oneLight} from "react-syntax-highlighter/dist/cjs/styles/prism";


IndicatorSlither.propTypes = {
    color: PropTypes.string,
    sx: PropTypes.object,
    vulnerabilitiesObject: PropTypes.object.isRequired,
};

export default function IndicatorSlither({

                                             vulnerabilitiesObject,
                                             color = 'background',
                                             sx,
                                             ...other
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
                <Typography variant="h3">Vulnerability Slither</Typography>
                <Typography variant="body1" sx={{lineHeight: 2}}>
                    {
                        vulnerabilitiesObject.map((vulnerability, index) => (
                            <Accordion key={index}>
                                <AccordionSummary
                                    expandIcon={<ExpandMoreIcon/>}
                                    aria-controls="panel1a-content"
                                    id="panel1a-header"
                                    sx={{background: "#FFE7D9"}}>
                                    <Typography
                                        variant="h6">{vulnerability.check} impact: {vulnerability.impact} confidence: {vulnerability.confidence}</Typography>
                                </AccordionSummary>
                                <AccordionDetails>
                                    <SyntaxHighlighter language="markdown" wrapLongLines style={oneLight}>
                                        {vulnerability.markdown}
                                    </SyntaxHighlighter>
                                </AccordionDetails>
                            </Accordion>
                        ))
                    }
                </Typography>

            </Card>
        </Grid>
    );

}
