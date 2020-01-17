import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { makeStyles } from '@material-ui/core/styles';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableRow from '@material-ui/core/TableRow';
import Paper from '@material-ui/core/Paper';
import Checkbox from '@material-ui/core/Checkbox';
import axios from 'axios';
import EnhancedTableHead from '../TableHead';
import EnhancedTableToolbar from '../TableToolbar';

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

function AgentsTable(props) {
  const { agents, setSnackbar, setSnackbarOpen } = props;
  const classes = useStyles();
  const [order, setOrder] = React.useState('asc');
  const [orderBy, setOrderBy] = React.useState('group');
  const [selected, setSelected] = React.useState([]);
  const [group, setGroup] = useState();

  const handleRequestSort = (event, property) => {
    const isDesc = orderBy === property && order === 'desc';
    setOrder(isDesc ? 'asc' : 'desc');
    setOrderBy(property);
  };

  const handleSelectAllClick = (event) => {
    if (event.target.checked) {
      const newSelecteds = agents.map((agent) => agent.identity);
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
      newSelected = newSelected.concat(
        selected.slice(0, selectedIndex),
        selected.slice(selectedIndex + 1),
      );
    }
    setSelected(newSelected);
  };

  const sendGrouping = () => {
    const url = `http://${process.env.REACT_APP_CONTROLLER_HOST}:8000/group`;
    axios.post(url, {
      group,
      agents: selected,
    })
      .then(() => {
        setSnackbar({ message: 'Grouping requested', type: 'success' });
        setSnackbarOpen(true);
      },
      () => {
        setSnackbar({ message: 'Grouping failed', type: 'error' });
        setSnackbarOpen(true);
      });
  };

  const isSelected = (name) => selected.indexOf(name) !== -1;

  return (
    <div className={classes.root}>
      <Paper className={classes.paper}>
        <EnhancedTableToolbar
          numSelected={selected.length}
          setGroup={setGroup}
          sendGrouping={sendGrouping}
        />
        <div className={classes.tableWrapper}>
          <Table
            className={classes.table}
            aria-labelledby="tableTitle"
            size="medium"
            aria-label="enhanced table"
          >
            <EnhancedTableHead
              classes={classes}
              numSelected={selected.length}
              order={order}
              orderBy={orderBy}
              onSelectAllClick={handleSelectAllClick}
              onRequestSort={handleRequestSort}
              rowCount={Object.keys(agents).length}
            />
            <TableBody>
              {stableSort(agents, getSorting(order, orderBy)).map((row) => {
                const isItemSelected = isSelected(row.identity);
                const labelId = `enhanced-table-checkbox-${row.identity}`;
                return (
                  <TableRow
                    hover
                    onClick={(event) => handleClick(event, row.identity)}
                    role="checkbox"
                    aria-checked={isItemSelected}
                    tabIndex={-1}
                    key={row.identity}
                    selected={isItemSelected}
                  >
                    <TableCell padding="checkbox">
                      <Checkbox
                        checked={isItemSelected}
                        inputProps={{ 'aria-labelledby': labelId }}
                      />
                    </TableCell>
                    <TableCell component="th" id={labelId} scope="row" padding="none">
                      {row.identity}
                    </TableCell>
                    <TableCell align="right">{row.group}</TableCell>
                    <TableCell align="right">{row.status}</TableCell>
                    <TableCell align="right">{row.cloned_repos}</TableCell>
                    <TableCell align="right">{row.test_running}</TableCell>
                    <TableCell align="right">{row.extra_info}</TableCell>
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

AgentsTable.propTypes = {
  agents: PropTypes.arrayOf(PropTypes.shape(
    {
      identity: PropTypes.string.isRequired,
      group: PropTypes.string.isRequired,
      status: PropTypes.string.isRequired,
      cloned_repos: PropTypes.array.isRequired,
      test_running: PropTypes.string.isRequired,
      extra_info: PropTypes.string.isRequired,
    },
  )).isRequired,
  setSnackbar: PropTypes.func.isRequired,
  setSnackbarOpen: PropTypes.func.isRequired,
};

export default React.memo(AgentsTable);
