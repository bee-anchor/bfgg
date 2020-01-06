import React from 'react';
import { Box } from '@material-ui/core';
import Paper from '@material-ui/core/Paper';
import { makeStyles } from '@material-ui/core/styles';
import GroupSelect from '../GroupSelect'
import EnhancedTable from '../AgentStatus';
import PropTypes from "prop-types";
import {grey} from "@material-ui/core/colors";

const useStyles = makeStyles({
  main: {
      padding: '2%',
      background: grey['200']
  },
});

export default function BodyAgents(props) {
  const classes = useStyles();
  const { groups, setSelectedGroup, selectedGroup, agents, setSnackbarOpen, setSnackbar } = props;

  return (
      <Paper varient='outlined'>
        <Box className={classes.main}>
            <GroupSelect groups={groups} setSelectedGroup={setSelectedGroup} selectedGroup={selectedGroup} />
            <EnhancedTable agents={agents} setSnackbarOpen={setSnackbarOpen} setSnackbar={setSnackbar} />
        </Box>
      </Paper>
  );
}

BodyAgents.propTypes = {
    groups: PropTypes.array.isRequired,
    setSelectedGroup: PropTypes.func.isRequired,
    selectedGroup: PropTypes.string.isRequired,
    agents: PropTypes.object.isRequired,
    setSnackbarOpen: PropTypes.func.isRequired,
    setSnackbar: PropTypes.func.isRequired,
};