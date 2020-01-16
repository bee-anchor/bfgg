import React from 'react';
import PropTypes from 'prop-types';
import clsx from 'clsx';
import { lighten, makeStyles } from '@material-ui/core/styles';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import IconButton from '@material-ui/core/IconButton';
import FormControl from '@material-ui/core/FormControl';
import InputAdornment from '@material-ui/core/InputAdornment';
import InputLabel from '@material-ui/core/InputLabel';
import OutlinedInput from '@material-ui/core/OutlinedInput';
import GroupWorkIcon from '@material-ui/icons/GroupWork';

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

export default function EnhancedTableToolbar(props) {
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
          {numSelected}
          {' '}
selected
        </Typography>
      ) : (
        <Typography className={classes.title} variant="h6" id="tableTitle">
              Connected Agents
        </Typography>
      )}

      {numSelected > 0
        && (
        <FormControl>
          <InputLabel htmlFor="group-name" variant="outlined">Group Name</InputLabel>
          <OutlinedInput
            id="group-name"
            type="text"
            labelWidth={100}
            onChange={(e) => setGroup(e.target.value)}
            endAdornment={(
              <InputAdornment position="end">
                <IconButton
                  onClick={sendGrouping}
                >
                  <GroupWorkIcon />
                </IconButton>
              </InputAdornment>
              )}
          />
        </FormControl>
        )}
    </Toolbar>
  );
}

EnhancedTableToolbar.propTypes = {
  numSelected: PropTypes.number.isRequired,
  setGroup: PropTypes.func.isRequired,
  sendGrouping: PropTypes.func.isRequired,
};
