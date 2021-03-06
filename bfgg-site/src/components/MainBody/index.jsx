import axios from 'axios';
import React, { useEffect, useState } from 'react';
import { Box } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import PropTypes from 'prop-types';
import useInterval from '../../hooks/useInterval';
import BodyAgents from '../BodyAgents';
import RunTab from '../RunTab';
import PastTab from '../PastTab';
import CustomSnackbar from '../CustomSnackbar';

const useStyles = makeStyles({
  main: {
    marginLeft: '160px',
  },
});

export default function MainBody(props) {
  const classes = useStyles();
  const [agents, setAgents] = useState([]);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbar, setSnackbar] = useState({ message: '', type: '' });
  const [groups, setGroups] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState('ungrouped');
  const [repo, setRepo] = useState();
  const [startName, setStartName] = useState();
  const [startTest, setStartTest] = useState();
  const [startJavaOpts, setStartJavaOpts] = useState();
  const { tabValue } = props;

  const handleAgents = (response) => {
    setAgents(response);
    const newGroups = [...new Set(Object.entries(response).map(
      ([, state]) => state.group,
    ))].sort();
    setGroups(newGroups);
    if (!newGroups.includes(selectedGroup)) {
      setSelectedGroup(newGroups[0]);
    }
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
      <BodyAgents
        groups={groups}
        setSelectedGroup={setSelectedGroup}
        selectedGroup={selectedGroup}
        agents={agents}
        setSnackbarOpen={setSnackbarOpen}
        setSnackbar={setSnackbar}
      />
      <RunTab
        tabValue={tabValue}
        setSnackbarOpen={setSnackbarOpen}
        setSnackbar={setSnackbar}
        selectedGroup={selectedGroup}
        repo={repo}
        setRepo={setRepo}
        startName={startName}
        setStartName={setStartName}
        startTest={startTest}
        setStartTest={setStartTest}
        startJavaOpts={startJavaOpts}
        setStartJavaOpts={setStartJavaOpts}
      />
      <PastTab
        tabValue={tabValue}
        setSnackbarOpen={setSnackbarOpen}
        setSnackbar={setSnackbar}
        selectedGroup={selectedGroup}
      />
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
