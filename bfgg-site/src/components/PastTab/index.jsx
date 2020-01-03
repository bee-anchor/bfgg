import React from 'react';
import { Box } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import CloneForm from '../CloneForm';
import StartForm from '../StartForm';
import StopForm from '../StopForm';
import PropTypes from "prop-types";
import TabPanel from "../TabPanel";

const useStyles = makeStyles({
  main: {
    padding: '2%',
  },
});

export default function RunTab(props) {
  const classes = useStyles();
  const { tabValue, setSnackbarOpen, setSnackbar, selectedGroup } = props;

  return (
      <TabPanel value={tabValue} index={0}>
        <Box className={classes.main}>
            <CloneForm setSnackbarOpen={setSnackbarOpen} setSnackbar={setSnackbar} selectedGroup={selectedGroup}/>
            <StartForm setSnackbarOpen={setSnackbarOpen} setSnackbar={setSnackbar} selectedGroup={selectedGroup}/>
            <StopForm setSnackbarOpen={setSnackbarOpen} setSnackbar={setSnackbar} selectedGroup={selectedGroup}/>
        </Box>
      </TabPanel>
  );
}

RunTab.propTypes = {
    tabValue: PropTypes.number.isRequired,
    setSnackbarOpen: PropTypes.func.isRequired,
    setSnackbar: PropTypes.func.isRequired,
    selectedGroup: PropTypes.string.isRequired,
};
