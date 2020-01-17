import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import clsx from 'clsx';
import { lighten, makeStyles } from '@material-ui/core/styles';
import TableContainer from '@material-ui/core/TableContainer';
import TablePagination from '@material-ui/core/TablePagination';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import TableSortLabel from '@material-ui/core/TableSortLabel';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import Paper from '@material-ui/core/Paper';
import IconButton from '@material-ui/core/IconButton';
import Tooltip from '@material-ui/core/Tooltip';
import RefreshIcon from '@material-ui/icons/Refresh';
import ReplayIcon from '@material-ui/icons/Replay';
import OpenInNewIcon from '@material-ui/icons/OpenInNew';
import axios from 'axios';

const headCells = [
  { id: 'TestId', label: 'Test Id' },
  { id: 'Project', label: 'Project' },
  { id: 'TestClass', label: 'Test Class' },
  { id: 'JavaOpts', label: 'Java Opts' },
  { id: 'StartTime', label: 'Start Time' },
  { id: 'EndTime', label: 'End Time' },
  { id: 'TestResults', label: 'Test Results' },
];

function desc(a, b, orderBy) {
  if (b[orderBy] < a[orderBy]) {
    return -1;
  }
  if (b[orderBy] > a[orderBy]) {
    return 1;
  }
  return 0;
}

function stableSort(array, cmp) {
  const stabilizedThis = array.map((el, index) => [el, index]);
  stabilizedThis.sort((a, b) => {
    const order = cmp(a[0], b[0]);
    if (order !== 0) return order;
    return a[1] - b[1];
  });
  return stabilizedThis.map((el) => el[0]);
}

function getSorting(order, orderBy) {
  return order === 'desc' ? (a, b) => desc(a, b, orderBy) : (a, b) => -desc(a, b, orderBy);
}

function EnhancedTableHead(props) {
  const {
    classes, order, orderBy, onRequestSort,
  } = props;
  const createSortHandler = (property) => (event) => {
    onRequestSort(event, property);
  };

  return (
      <TableHead>
        <TableRow>
          <TableCell
              key="rerun"
              align="center"
              padding="default"
          />
          {headCells.map((headCell) => (
              <TableCell
                  key={headCell.id}
                  align="center"
                  padding="default"
                  sortDirection={orderBy === headCell.id ? order : false}
              >
                <TableSortLabel
                    active={orderBy === headCell.id}
                    direction={order}
                    onClick={createSortHandler(headCell.id)}
                >
                  {headCell.label}
                  {orderBy === headCell.id ? (
                      <span className={classes.visuallyHidden}>
                  {order === 'desc' ? 'sorted descending' : 'sorted ascending'}
                </span>
                  ) : null}
                </TableSortLabel>
              </TableCell>
          ))}
        </TableRow>
      </TableHead>
  );
}

EnhancedTableHead.propTypes = {
  classes: PropTypes.shape({
    visuallyHidden: PropTypes.string,
  }).isRequired,
  onRequestSort: PropTypes.func.isRequired,
  order: PropTypes.oneOf(['asc', 'desc']).isRequired,
  orderBy: PropTypes.string.isRequired,
};

const useToolbarStyles = makeStyles((theme) => ({
  root: {
    paddingLeft: theme.spacing(2),
    paddingRight: theme.spacing(1),
    marginTop: theme.spacing(2),
  },
  highlight:
      theme.palette.type === 'light'
          ? {
            color: theme.palette.secondary.main,
            backgroundColor: lighten(theme.palette.secondary.light, 0.85),
          }
          : {
            color: theme.palette.text.primary,
            backgroundColor: theme.palette.secondary.dark,
          },
  title: {
    flex: '1 1 100%',
  },
}));

const EnhancedTableToolbar = (props) => {
  const classes = useToolbarStyles();
  const { getPastTests } = props;

  return (
      <Toolbar
          className={clsx(classes.root)}
      >
        <Typography className={classes.title} variant="h6" id="testsTableTitle">
          Past Tests
        </Typography>
        <Tooltip title="Refresh">
          <IconButton onClick={getPastTests}>
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Toolbar>
  );
};

EnhancedTableToolbar.propTypes = {
  getPastTests: PropTypes.func.isRequired,
};

const useStyles = makeStyles((theme) => ({
  root: {
    width: '100%',
  },
  paper: {
    width: '100%',
    marginBottom: theme.spacing(2),
  },
  table: {
    minWidth: 750,
  },
  tableWrapper: {
    overflowX: 'auto',
  },
  visuallyHidden: {
    border: 0,
    clip: 'rect(0 0 0 0)',
    height: 1,
    margin: -1,
    overflow: 'hidden',
    padding: 0,
    position: 'absolute',
    top: 20,
    width: 1,
  },
}));

function PastTestsTable(props) {
  const { selectedGroup, setSnackbar, setSnackbarOpen } = props;
  const classes = useStyles();
  const [order, setOrder] = React.useState('desc');
  const [orderBy, setOrderBy] = React.useState('StartTime');
  const [tests, setTests] = useState([]);
  const [page, setPage] = React.useState(0);
  const [rowsPerPage, setRowsPerPage] = React.useState(5);

  const handleRequestSort = (event, property) => {
    const isDesc = orderBy === property && order === 'desc';
    setOrder(isDesc ? 'asc' : 'desc');
    setOrderBy(property);
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = event => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const getPastTests = () => {
    const url = `http://${process.env.REACT_APP_CONTROLLER_HOST}:8000/past-tests`;
    axios.get(url)
        .then((res) => setTests(res.data));
  };

  const handleRequestRerun = (project, testClass, javaOpts) => {
    const url = `http://${process.env.REACT_APP_CONTROLLER_HOST}:8000/start`;
    axios.post(url, {
      group: selectedGroup,
      project: project,
      testClass: testClass,
      javaOpts,
    })
        .then(() => {
              setSnackbar({ message: 'Start test requested', type: 'success' });
              setSnackbarOpen(true);
            },
            () => {
              setSnackbar({ message: 'Failed to start test', type: 'error' });
              setSnackbarOpen(true);
            });
  };

  useEffect(() => {
    getPastTests();
  }, []);

  return (
      <div className={classes.root}>
        <Paper className={classes.paper}>
          <EnhancedTableToolbar getPastTests={getPastTests} />
          <div className={classes.tableWrapper}>
            <TableContainer>
              <Table
                  className={classes.table}
                  aria-labelledby="testsTableTitle"
                  size="medium"
                  aria-label="past tests table"
              >
                <EnhancedTableHead
                    classes={classes}
                    order={order}
                    orderBy={orderBy}
                    onRequestSort={handleRequestSort}
                />
                <TableBody>
                  {stableSort(tests, getSorting(order, orderBy))
                      .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                      .map((test) => (
                      <TableRow
                          hover
                          key={test.TestId}
                      >
                        <TableCell align="center">
                          <Tooltip title="Re-run Test">
                            <IconButton
                                onClick={() => handleRequestRerun(test.Project, test.TestClass, test.JavaOpts)}
                                aria-label="re-run test"
                            >
                              <ReplayIcon/>
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                        <TableCell align="center">{test.TestId}</TableCell>
                        <TableCell align="center">{test.Project}</TableCell>
                        <TableCell align="center">{test.TestClass}</TableCell>
                        <TableCell align="center">{test.JavaOpts}</TableCell>
                        <TableCell align="left">{test.StartTime}</TableCell>
                        <TableCell align="left">{test.EndTime}</TableCell>
                        <TableCell align="center">
                          {Object.prototype.hasOwnProperty.call(test, 'TestResultsUrl') ? (
                              <a target="_blank" rel="noopener noreferrer" href={test.TestResultsUrl}><OpenInNewIcon aria-label="open in new tab" /></a>
                          ) : ('')}
                        </TableCell>
                      </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
                rowsPerPageOptions={[5, 20, 50]}
                component="div"
                count={tests.length}
                rowsPerPage={rowsPerPage}
                page={page}
                onChangePage={handleChangePage}
                onChangeRowsPerPage={handleChangeRowsPerPage}
            />
          </div>
        </Paper>
      </div>
  );
}

PastTestsTable.propTypes = {
  selectedGroup: PropTypes.string.isRequired,
  setSnackbar: PropTypes.func.isRequired,
  setSnackbarOpen: PropTypes.func.isRequired,
};

export default React.memo(PastTestsTable);
