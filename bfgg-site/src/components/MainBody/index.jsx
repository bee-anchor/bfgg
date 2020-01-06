import axios from 'axios';
import React, { useEffect, useState } from 'react';
import { Box } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import useInterval from '../../hooks/useInterval';
import BodyAgents from '../BodyAgents';
import RunTab from '../RunTab';
import PastTab from '../PastTab';
import CustomSnackbar from '../CustomSnackbar';
import PropTypes from "prop-types";

const useStyles = makeStyles({
  main: {
    marginLeft: '160px',
  },
});

export default function MainBody(props) {
  const classes = useStyles();
  const [agents, setAgents] = useState({});
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbar, setSnackbar] = useState({ message: '', type: '' });
  const [groups, setGroups] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState('ungrouped');
  const { tabValue } = props;

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
      <Box className={classes.main}>
          <BodyAgents groups={groups} setSelectedGroup={setSelectedGroup} selectedGroup={selectedGroup}
                      agents={agents} setSnackbarOpen={setSnackbarOpen} setSnackbar={setSnackbar} />
          <RunTab tabValue={tabValue} setSnackbarOpen={setSnackbarOpen} setSnackbar={setSnackbar} selectedGroup={selectedGroup}/>
          <PastTab tabValue={tabValue} setSnackbarOpen={setSnackbarOpen} setSnackbar={setSnackbar} selectedGroup={selectedGroup}/>
          <CustomSnackbar
              setSnackbarOpen={setSnackbarOpen}
              snackbarOpen={snackbarOpen}
              message={snackbar.message}
              type={snackbar.type}
          />
      </Box>
  );
}

MainBody.propTypes = {
    tabValue: PropTypes.number.isRequired,
};
