// @mui
import PropTypes from 'prop-types';
import {Accordion, AccordionDetails, AccordionSummary, Card, Typography} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import {Prism as SyntaxHighlighter} from 'react-syntax-highlighter';
import {oneLight} from "react-syntax-highlighter/dist/cjs/styles/prism";


IndicatorVerifiedContract.propTypes = {
    color: PropTypes.string,
    sx: PropTypes.object,
    verifiedContractObject: PropTypes.object.isRequired,
};

export default function IndicatorVerifiedContract({

                                                      verifiedContractObject,
                                                      color = 'background', sx, ...other
                                                  }) {
    function checkIfVerifiedContract(verifiedContractObject) {
        if (verifiedContractObject.verifiedContract !== "") {
            return (

                <Typography variant="body1" sx={{lineHeight: 2}}>
                    <b>Compiler
                        Version:</b> {verifiedContractObject.CompilerVersion === "" ? "Not Defined" : verifiedContractObject.CompilerVersion}
                    <br/>
                    <b>EVMVersion:</b> {verifiedContractObject.EVMVersion === "" ? "Not Defined" : verifiedContractObject.EVMVersion}
                    <br/>
                    <b>Proxy: </b> {verifiedContractObject.Proxy === 0 ? "No" : "Yes"} <br/> <br/>
                    <Accordion>
                        <AccordionSummary
                            expandIcon={<ExpandMoreIcon/>}
                            aria-controls="panel1a-content"
                            id="panel1a-header"
                            sx={{background: "#FFE7D9"}}
                        >
                            <Typography variant="h6">Constructor Arguments:</Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                            <SyntaxHighlighter language="json" style={oneLight} wrapLongLines>
                                {verifiedContractObject.ConstructorArguments === "" ? "Not Defined" : verifiedContractObject.ConstructorArguments}
                            </SyntaxHighlighter>
                        </AccordionDetails>
                    </Accordion>
                    <Accordion>
                        <AccordionSummary
                            expandIcon={<ExpandMoreIcon/>}
                            aria-controls="panel1a-content"
                            id="panel1a-header"
                            sx={{background: "#FFE7D9"}}
                        >
                            <Typography variant="h6">ABI</Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                            <SyntaxHighlighter language="json" style={oneLight} wrapLongLines>
                                {verifiedContractObject.ABI}
                            </SyntaxHighlighter>
                        </AccordionDetails>
                    </Accordion>
                    <Accordion>
                        <AccordionSummary
                            expandIcon={<ExpandMoreIcon/>}
                            aria-controls="panel1a-content"
                            id="panel1a-header"
                            sx={{background: "#FFE7D9"}}
                        >
                            <Typography variant="h6">Source Code</Typography>
                        </AccordionSummary>
                        <AccordionDetails>

                            <SyntaxHighlighter language="solidity" style={oneLight} wrapLines wrapLongLines
                                               showLineNumbers>
                                {verifiedContractObject.SourceCode}
                            </SyntaxHighlighter>

                        </AccordionDetails>
                    </Accordion>
                </Typography>

            )
        }

        return (

            <Typography variant="body1" sx={{lineHeight: 2}}>
                <b>Smart Contract is not verified!</b>
            </Typography>
        )
    }

    return (

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
            <Typography variant="h3">Verified Contract</Typography>
            {
                checkIfVerifiedContract(verifiedContractObject)
            }

        </Card>
    );

}
