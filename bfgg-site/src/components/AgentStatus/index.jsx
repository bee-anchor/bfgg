import React, {useState} from 'react';
import PropTypes from 'prop-types';
import clsx from 'clsx';
import { lighten, makeStyles } from '@material-ui/core/styles';
import Box from '@material-ui/core/Box'
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import TableSortLabel from '@material-ui/core/TableSortLabel';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import Paper from '@material-ui/core/Paper';
import Checkbox from '@material-ui/core/Checkbox';
import IconButton from '@material-ui/core/IconButton';
import FormControl from '@material-ui/core/FormControl';
import InputAdornment from '@material-ui/core/InputAdornment';
import InputLabel from '@material-ui/core/InputLabel';
import OutlinedInput from '@material-ui/core/OutlinedInput';
import GroupWorkIcon from '@material-ui/icons/GroupWork';
import axios from "axios";

const headCells = [
  { id: 'identity', numeric: false, disablePadding: true, label: 'Identity' },
  { id: 'group', numeric: true, disablePadding: false, label: 'Group' },
  { id: 'status', numeric: true, disablePadding: false, label: 'Status' },
  { id: 'clonedRepos', numeric: true, disablePadding: false, label: 'Cloned Repos' },
  { id: 'testRunning', numeric: true, disablePadding: false, label: 'Test Running' },
  { id: 'extraInfo', numeric: true, disablePadding: false, label: 'Extra Info' },
];

function EnhancedTableHead(props) {
  const { classes, onSelectAllClick, order, orderBy, numSelected, rowCount, onRequestSort } = props;
  const createSortHandler = property => event => {
    onRequestSort(event, property);
  };

  return (
      <TableHead>
        <TableRow>
          <TableCell padding="checkbox">
            <Checkbox
                indeterminate={numSelected > 0 && numSelected < rowCount}
                checked={numSelected === rowCount}
                onChange={onSelectAllClick}
                inputProps={{ 'aria-label': 'select all desserts' }}
            />
          </TableCell>
          {headCells.map(headCell => (
              <TableCell
                  key={headCell.id}
                  align={headCell.numeric ? 'right' : 'left'}
                  padding={headCell.disablePadding ? 'none' : 'default'}
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
  numSelected: PropTypes.number.isRequired,
  onRequestSort: PropTypes.func.isRequired,
  onSelectAllClick: PropTypes.func.isRequired,
  order: PropTypes.oneOf(['asc', 'desc']).isRequired,
  orderBy: PropTypes.string.isRequired,
  rowCount: PropTypes.number.isRequired,
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

const EnhancedTableToolbar = props => {
  const classes = useToolbarStyles();
  const { numSelected, setGroup, sendGrouping } = props;



  return (
      <Toolbar
          className={clsx(classes.root, {
            [classes.highlight]: numSelected > 0,
          })}
      >
        {numSelected > 0 ? (
            <Typography className={classes.title} color="inherit" variant="subtitle1">
              {numSelected} selected
            </Typography>
        ) : (
            <Typography className={classes.title} variant="h6" id="tableTitle">
              Connected Agents
            </Typography>
        )}

        {numSelected > 0 &&
        <FormControl>
          <InputLabel htmlFor="group-name" variant="outlined">Group Name</InputLabel>
          <OutlinedInput
              id="group-name"
              type="text"
              labelWidth={100}
              onChange={(e) => setGroup(e.target.value)}
              endAdornment={
                <InputAdornment position="end">
                  <IconButton
                      onClick={sendGrouping}
                  >
                    <GroupWorkIcon/>
                  </IconButton>
                </InputAdornment>
              }
          />
        </FormControl>
        }
      </Toolbar>
  );
};

EnhancedTableToolbar.propTypes = {
  numSelected: PropTypes.number.isRequired,
  setGroup: PropTypes.func.isRequired,
  sendGrouping: PropTypes.func.isRequired,
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

export default function EnhancedTable(props) {
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

  const handleSelectAllClick = event => {
    if (event.target.checked) {
      const newSelecteds = Object.entries(agents).map(([identity, state]) => identity);
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
      "group": group,
      "agents": selected
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

  const isSelected = name => selected.indexOf(name) !== -1;

  return (
      <div className={classes.root}>
        <Paper className={classes.paper}>
          <EnhancedTableToolbar numSelected={selected.length} setGroup={setGroup} sendGrouping={sendGrouping} />
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
                  rowCount={agents.length}
              />
              <TableBody>
                {Object.entries(agents).map(([identity, state]) => {
                      const isItemSelected = isSelected(identity);
                      const labelId = `enhanced-table-checkbox-${identity}`;
                      return (
                          <TableRow
                              hover
                              onClick={event => handleClick(event, identity)}
                              role="checkbox"
                              aria-checked={isItemSelected}
                              tabIndex={-1}
                              key={identity}
                              selected={isItemSelected}
                          >
                            <TableCell padding="checkbox">
                              <Checkbox
                                  checked={isItemSelected}
                                  inputProps={{ 'aria-labelledby': labelId }}
                              />
                            </TableCell>
                            <TableCell component="th" id={labelId} scope="row" padding="none">
                              {identity}
                            </TableCell>
                            <TableCell align="right">{state['group']}</TableCell>
                            <TableCell align="right">{state['status']}</TableCell>
                            <TableCell align="right">{state['cloned_repos']}</TableCell>
                            <TableCell align="right">{state['test_running']}</TableCell>
                            <TableCell align="right">{state['extra_info']}</TableCell>
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

EnhancedTable.propTypes = {
  agents: PropTypes.object.isRequired,
  setSnackbar: PropTypes.func.isRequired,
  setSnackbarOpen: PropTypes.func.isRequired,
};
