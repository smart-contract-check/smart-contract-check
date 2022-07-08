
export function unixTimeStampToDateTime(unixTimeStamp){
    // https://stackoverflow.com/questions/847185/convert-a-unix-timestamp-to-time-in-javascript
    if (unixTimeStamp == null) {
        return 0
    }
    return new Date(unixTimeStamp * 1000).toISOString().slice(0, 19).replace('T', ' ')
}

export function createWalletAddressURL(address) {
    return (
        <a href={`https://etherscan.io/address/${address}`} target="_blank" rel="noreferrer">
            {address}
        </a>
    )
}

export function createTransactionURL(transactionHash) {
    return (
        <a href={`https://etherscan.io/tx/${transactionHash}`} target="_blank" rel="noreferrer">
            {transactionHash}
        </a>
    )
}

export function createTokenURL(tokenAddress) {
    return (
        <a href={`https://etherscan.io/token/${tokenAddress}`} target="_blank" rel="noreferrer">
            {tokenAddress}
        </a>
    )
}