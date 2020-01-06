import React, {useEffect, useState} from 'react';
import PropTypes from 'prop-types';
import clsx from 'clsx';
import { lighten, makeStyles } from '@material-ui/core/styles';
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
import RefreshIcon from '@material-ui/icons/Refresh';
import OpenInNewIcon from '@material-ui/icons/OpenInNew';
import axios from "axios";

const headCells = [
  { id: 'testId', label: 'Test Id' },
  { id: 'project', label: 'Project' },
  { id: 'testClass', label: 'Test Class' },
  { id: 'javaOpts', label: 'Java Opts' },
  { id: 'startTime', label: 'Start Time' },
  { id: 'endTime', label: 'End Time' },
  { id: 'testResults', label: 'Test Results' },
];

function EnhancedTableHead(props) {
  const { classes, order, orderBy, onRequestSort } = props;
  const createSortHandler = property => event => {
    onRequestSort(event, property);
  };

  return (
      <TableHead>
        <TableRow>
          {headCells.map(headCell => (
              <TableCell
                  key={headCell.id}
                  align='center'
                  padding='default'
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
  classes: PropTypes.object.isRequired,
  onRequestSort: PropTypes.func.isRequired,
  order: PropTypes.oneOf(['asc', 'desc']).isRequired,
  orderBy: PropTypes.string.isRequired,
};

const useToolbarStyles = makeStyles(theme => ({
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
        <IconButton onClick={getPastTests}>
          <RefreshIcon/>
        </IconButton>
      </Toolbar>
  );
};

EnhancedTableToolbar.propTypes = {
  getPastTests: PropTypes.func.isRequired,
};

const useStyles = makeStyles(theme => ({
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

export default function PastTestsTable(props) {
  const {selectedGroup, setSnackbar, setSnackbarOpen } = props;
  const classes = useStyles();
  const [order, setOrder] = React.useState('asc');
  const [orderBy, setOrderBy] = React.useState('StartTime');
  const [ tests, setTests ] = useState([]);

  const handleRequestSort = (event, property) => {
    const isDesc = orderBy === property && order === 'desc';
    setOrder(isDesc ? 'asc' : 'desc');
    setOrderBy(property);
  };

  const getPastTests = () => {
    const url = `http://${process.env.REACT_APP_CONTROLLER_HOST}:8000/past-tests`;
    axios.get(url)
        .then((res) => setTests(res.data));
  };

  useEffect(() => {
    getPastTests()
  }, []);

  return (
      <div className={classes.root}>
        <Paper className={classes.paper}>
          <EnhancedTableToolbar getPastTests={getPastTests}/>
          <div className={classes.tableWrapper}>
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
                {tests.map( (test) => {
                  return (
                      <TableRow
                          hover
                          key={test['TestId']}
                      >
                        <TableCell align="center">{test['TestId']}</TableCell>
                        <TableCell align="center">{test['Project']}</TableCell>
                        <TableCell align="center">{test['TestClass']}</TableCell>
                        <TableCell align="center">{test['javaOpts']}</TableCell>
                        <TableCell align="left">{test['StartTime']}</TableCell>
                        <TableCell align="left">{test['EndTime']}</TableCell>
                        <TableCell align="center">
                          {test.hasOwnProperty('TestResultsUrl') ? (
                              <a target="_blank" href={test['TestResultsUrl']}><OpenInNewIcon/></a>
                          ) : ("")}
                        </TableCell>
                      </TableRow>
                  );
                })}
              </TableBody>
            </Table>
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
