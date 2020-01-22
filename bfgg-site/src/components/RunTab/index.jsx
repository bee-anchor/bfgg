import React from 'react';
import { Box } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import PropTypes from 'prop-types';
import CloneForm from '../CloneForm';
import StartForm from '../StartForm';
import StopForm from '../StopForm';
import TabPanel from '../TabPanel';

const useStyles = makeStyles({
  main: {
    padding: '2%',
  },
});

export default function RunTab(props) {
  const classes = useStyles();
  const {
    tabValue, setSnackbarOpen, setSnackbar, selectedGroup,
    repo, setRepo, startName, setStartName, startTest, setStartTest,
    startJavaOpts, setStartJavaOpts
  } = props;

  return (
    <TabPanel value={tabValue} index={0}>
      <Box className={classes.main}>
        <CloneForm
          setSnackbarOpen={setSnackbarOpen}
          setSnackbar={setSnackbar}
          selectedGroup={selectedGroup}
          repo={repo}
          setRepo={setRepo}
        />
        <StartForm
          setSnackbarOpen={setSnackbarOpen}
          setSnackbar={setSnackbar}
          selectedGroup={selectedGroup}
          name={startName}
          setName={setStartName}
          test={startTest}
          setTest={setStartTest}
          javaOpts={startJavaOpts}
          setJavaOpts={setStartJavaOpts}
        />
        <StopForm
          setSnackbarOpen={setSnackbarOpen}
          setSnackbar={setSnackbar}
          selectedGroup={selectedGroup}
        />
      </Box>
    </TabPanel>
  );
}

RunTab.propTypes = {
  tabValue: PropTypes.number.isRequired,
  setSnackbarOpen: PropTypes.func.isRequired,
  setSnackbar: PropTypes.func.isRequired,
  selectedGroup: PropTypes.string.isRequired,
  repo: PropTypes.string.isRequired,
  setRepo: PropTypes.func.isRequired,
  startName: PropTypes.string.isRequired,
  setStartName: PropTypes.func.isRequired,
  startTest: PropTypes.string.isRequired,
  setStartTest: PropTypes.func.isRequired,
  startJavaOpts: PropTypes.string.isRequired,
  setStartJavaOpts: PropTypes.func.isRequired,
};
