import axios from 'axios';
import React, { useEffect, useState } from 'react';
import { Box } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import useInterval from '../../hooks/useInterval';
import GroupSelect from '../GroupSelect'
import EnhancedTable from '../AgentStatus';
import CloneForm from '../CloneForm';
import StartForm from '../StartForm';
import StopForm from '../StopForm';
import CustomSnackbar from '../CustomSnackbar';

const useStyles = makeStyles({
  main: {
    marginLeft: '20%',
  },
});

export default function MainBody() {
  const classes = useStyles();
  const [agents, setAgents] = useState({});
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbar, setSnackbar] = useState({ message: '', type: '' });
  const [groups, setGroups] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState('ungrouped');

  const handleAgents = (response) => {
      setAgents(response);
      setGroups([...new Set(Object.entries(agents).map(([identity, state]) => state.group))].sort());
  };

  const getAgentState = () => {
    const url = `http://${process.env.REACT_APP_CONTROLLER_HOST}:8000/status`;
    axios.get(url)
      .then((res) => handleAgents(res.data));
  };

  useEffect(() => getAgentState(), []);

  useInterval(
    () => getAgentState(),
    5000,
  );

  return (
    <Box padding="2%" className={classes.main}>
        <GroupSelect groups={groups} setSelectedGroup={setSelectedGroup} selectedGroup={selectedGroup} />
        <EnhancedTable agents={agents} setSnackbarOpen={setSnackbarOpen} setSnackbar={setSnackbar} />
        <CloneForm setSnackbarOpen={setSnackbarOpen} setSnackbar={setSnackbar} selectedGroup={selectedGroup}/>
        <StartForm setSnackbarOpen={setSnackbarOpen} setSnackbar={setSnackbar} selectedGroup={selectedGroup}/>
        <StopForm setSnackbarOpen={setSnackbarOpen} setSnackbar={setSnackbar} selectedGroup={selectedGroup}/>
      <CustomSnackbar
        setSnackbarOpen={setSnackbarOpen}
        snackbarOpen={snackbarOpen}
        message={snackbar.message}
        type={snackbar.type}
      />
    </Box>
  );
}
