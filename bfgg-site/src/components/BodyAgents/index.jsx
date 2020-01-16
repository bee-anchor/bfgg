import React from 'react';
import { Box } from '@material-ui/core';
import Paper from '@material-ui/core/Paper';
import { makeStyles } from '@material-ui/core/styles';
import PropTypes from 'prop-types';
import { grey } from '@material-ui/core/colors';
import GroupSelect from '../GroupSelect';
import AgentsTable from '../AgentStatus/Table';

const useStyles = makeStyles({
  main: {
    padding: '2%',
    background: grey['200'],
  },
});

export default function BodyAgents(props) {
  const classes = useStyles();
  const {
    groups, setSelectedGroup, selectedGroup, agents, setSnackbarOpen, setSnackbar,
  } = props;

  return (
    <Paper varient="outlined">
      <Box className={classes.main}>
        <GroupSelect
          groups={groups}
          setSelectedGroup={setSelectedGroup}
          selectedGroup={selectedGroup}
        />
        <AgentsTable
          agents={agents}
          setSnackbarOpen={setSnackbarOpen}
          setSnackbar={setSnackbar}
        />
      </Box>
    </Paper>
  );
}

BodyAgents.propTypes = {
  groups: PropTypes.arrayOf(PropTypes.string).isRequired,
  setSelectedGroup: PropTypes.func.isRequired,
  selectedGroup: PropTypes.string.isRequired,
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
  setSnackbarOpen: PropTypes.func.isRequired,
  setSnackbar: PropTypes.func.isRequired,
};
