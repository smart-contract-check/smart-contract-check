import {filter} from 'lodash';
import {useEffect, useState} from 'react';
// material
import {
    Card,
    Container,
    Stack,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TablePagination,
    TableRow,
    Typography,
} from '@mui/material';
// components
import Page from '../components/Page';
import Scrollbar from '../components/Scrollbar';
import SearchNotFound from '../components/SearchNotFound';
import {UserListHead} from '../sections/@dashboard/user';
import {fShortenNumber} from "../utils/formatNumber";
import {unixTimeStampToDateTime} from "../helperFunction";


// ----------------------------------------------------------------------

const TABLE_HEAD = [
    {id: 'scan_time', label: 'Scan Time (UTC)', alignRight: false},
    {id: 'symbol', label: 'Symbol', alignRight: false},
    {id: 'name', label: 'Name', alignRight: false},
    {id: 'address', label: 'Address', alignRight: false},
    {id: 'custom_scam_probability', label: 'Custom Score', alignRight: false},
    {id: 'svm_scam_probability', label: 'SVM Score', alignRight: false},
    {id: 'xgboost_scam_probability', label: 'XGB Score', alignRight: false},
];

const TABLE_COUNT = 10;
const ROWS_PER_PAGE_OPTIONS = [10, 25, 50, 100]


function Example() {
    // Declare a new state variable, which we'll call "count"
    const [count, setCount] = useState(0);

    return count;
}

// ----------------------------------------------------------------------

function descendingComparator(a, b, orderBy) {
    if (b[orderBy] < a[orderBy]) {
        return -1;
    }
    if (b[orderBy] > a[orderBy]) {
        return 1;
    }
    return 0;
}

function getComparator(order, orderBy) {
    return order === 'desc'
        ? (a, b) => descendingComparator(a, b, orderBy)
        : (a, b) => -descendingComparator(a, b, orderBy);
}

function applySortFilter(array, comparator, query) {
    const stabilizedThis = array.map((el, index) => [el, index]);
    stabilizedThis.sort((a, b) => {
        const order = comparator(a[0], b[0]);
        if (order !== 0) return order;
        return a[1] - b[1];
    });
    if (query) {
        return filter(array, (_user) => _user.name.toLowerCase().indexOf(query.toLowerCase()) !== -1);
    }
    return stabilizedThis.map((el) => el[0]);
}

export default function User() {
    const [page, setPage] = useState(0);
    const [tokenCount, setTokenCount] = useState(100);

    const [order, setOrder] = useState('desc');

    // const [selected, setSelected] = useState([]);

    const [orderBy, setOrderBy] = useState('scan_time');

    const [filterName, setFilterName] = useState('');

    const [rowsPerPage, setRowsPerPage] = useState(TABLE_COUNT);

    const handleRequestSort = (event, property) => {
        const isAsc = orderBy === property && order === 'asc';
        setOrder(isAsc ? 'desc' : 'asc');
        setOrderBy(property);
    };

// API call
    const [TokenList, setTokenList] = useState([]);

    useEffect(() => {
        const loadTokenList = async () => {
            try {
                const response = await fetch(`${process.env.REACT_APP_BACKEND_URL_WITH_PORT}/getRecentScans?page_num=${page}&page_size=${rowsPerPage}`);
                const json = await response.json()
                setTokenList(json)
                setTokenCount(json?.[json.length - 1].pagination.maxItems)
            } catch (error) {
                console.log(error)
            }
        }
        loadTokenList()
    }, [rowsPerPage, page])


    /*
    const handleSelectAllClick = (event) => {
      if (event.target.checked) {
        const newSelecteds = USERLIST.map((n) => n.name);
        setSelected(newSelecteds);
        return;
      }
      setSelected([]);
    };

    const handleClick = (event, name) => {
      const selectedIndex = selected.indexOf(name);
      let newSelected = [];
      if (selectedIndex === -1) {
        newSelected = newSelected.concat(selected, name);
      } else if (selectedIndex === 0) {
        newSelected = newSelected.concat(selected.slice(1));
      } else if (selectedIndex === selected.length - 1) {
        newSelected = newSelected.concat(selected.slice(0, -1));
      } else if (selectedIndex > 0) {
        newSelected = newSelected.concat(selected.slice(0, selectedIndex), selected.slice(selectedIndex + 1));
      }
      setSelected(newSelected);
    };

     */

    const handleChangePage = (event, newPage) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(1);
    };

    const handleFilterByName = (event) => {
        setFilterName(event.target.value);
    };

    const emptyRows = 1 // page > 0 ? Math.max(0, (1 + page) * rowsPerPage - TokenList.length) : 0;

    const filteredTokens = applySortFilter(TokenList, getComparator(order, orderBy), filterName);

    const isUserNotFound = filteredTokens.length === 0;
    return (
        <Page title="Recent Indexed">
            <Container>
                <Stack direction="row" alignItems="center" justifyContent="space-between" mb={5}>
                    <Typography variant="h4" gutterBottom>
                        Smart Contract Overview
                    </Typography>
                </Stack>

                <Card>
                    {/*
          <UserListToolbar numSelected={selected.length} filterName={filterName} onFilterName={handleFilterByName} />
          */}

                    <Scrollbar>
                        <TableContainer sx={{minWidth: 800}}>
                            <Table>
                                <UserListHead

                                    order={order}
                                    orderBy={orderBy}
                                    headLabel={TABLE_HEAD}
                                    rowCount={TokenList.length}
                                    // numSelected={selected.length}
                                    onRequestSort={handleRequestSort}
                                    // onSelectAllClick={handleSelectAllClick}
                                />
                                <TableBody>
                                    {filteredTokens.map((row, index) => {

                                        const {
                                            address,
                                            name,
                                            symbol,
                                            scan_time: scanTime,
                                            custom_score: customScore,
                                            svm_score: svmScore,
                                            xgb_score: xgboostScore,
                                        } = row;
                                        // const isItemSelected = selected.indexOf(name) !== -1;

                                        return (
                                            scanTime !== undefined && (
                                                <TableRow
                                                    hover
                                                    key={address}
                                                    tabIndex={-1}
                                                    role="checkbox"
                                                    onClick={() => {
                                                        let url = window.location.origin;
                                                        url += `/dashboard/token-list/${address}`
                                                        window.location = url;
                                                    }}
                                                    style={{cursor: 'pointer'}}
                                                    // selected={isItemSelected}
                                                    // aria-checked={isItemSelected}
                                                >
                                                    {/*
                        <TableCell padding="checkbox">
                          <Checkbox checked={isItemSelected} onChange={(event) => handleClick(event, name)} />
                        </TableCell>
                        */}
                                                    { /*
                        <TableCell component="th" scope="row" padding="normal">

                          <Stack direction="row" alignItems="center" spacing={2}>
                             <Avatar alt={name} src={avatarUrl} />
                            <Typography variant="subtitle2" noWrap>
                              {name}
                            </Typography>
                          </Stack>

                        </TableCell>
                        */}
                                                    <TableCell align="left"> </TableCell>
                                                    <TableCell align="left">{
                                                        unixTimeStampToDateTime(scanTime)

                                                    }</TableCell>
                                                    <TableCell align="left">{symbol}</TableCell>
                                                    <TableCell align="left">{name}</TableCell>
                                                    <TableCell align="left">{address}</TableCell>
                                                    <TableCell align="left">{fShortenNumber(customScore * 100)}</TableCell>
                                                    <TableCell align="left">{fShortenNumber(svmScore * 100)}</TableCell>
                                                    <TableCell align="left">{fShortenNumber(xgboostScore * 100)}</TableCell>

                                                    { /* <TableCell align="left">{isVerified ? 'Yes' : 'No'}</TableCell>

                        <TableCell align="left">
                          <Label variant="ghost" color={(status === 'banned' && 'error') || 'success'}>
                            {sentenceCase(status)}
                          </Label>
                        </TableCell>
                        <TableCell align="right">
                          <UserMoreMenu />
                        </TableCell>
                        */}
                                                </TableRow>

                                            ));
                                    })}
                                    {emptyRows > 0 && (
                                        <TableRow style={{height: 53 * emptyRows}}>
                                            <TableCell colSpan={6}/>
                                        </TableRow>
                                    )}
                                </TableBody>


                                {isUserNotFound && (
                                    <TableBody>
                                        <TableRow>
                                            <TableCell align="center" colSpan={6} sx={{py: 3}}>
                                                <SearchNotFound searchQuery={filterName}/>
                                            </TableCell>
                                        </TableRow>
                                    </TableBody>
                                )}
                            </Table>
                        </TableContainer>
                    </Scrollbar>

                    <TablePagination
                        rowsPerPageOptions={ROWS_PER_PAGE_OPTIONS}
                        component="div"
                        count={tokenCount}
                        rowsPerPage={rowsPerPage}
                        page={page}
                        onPageChange={handleChangePage}
                        onRowsPerPageChange={handleChangeRowsPerPage}
                    />
                </Card>
            </Container>
        </Page>
    );
}
