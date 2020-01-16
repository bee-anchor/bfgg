import React from 'react';
import { Box } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import PropTypes from 'prop-types';
import TabPanel from '../TabPanel';
import PastTestsTable from '../PastTestsTable';

const useStyles = makeStyles({
  main: {
    padding: '2%',
  },
});

export default function PastTab(props) {
  const classes = useStyles();
  const {
    tabValue, setSnackbarOpen, setSnackbar, selectedGroup,
  } = props;


  return (
    <TabPanel value={tabValue} index={1}>
      <Box className={classes.main}>
        <PastTestsTable
          selectedGroup={selectedGroup}
          setSnackbar={setSnackbar}
          setSnackbarOpen={setSnackbarOpen}
        />
      </Box>
    </TabPanel>
  );
}

PastTab.propTypes = {
  tabValue: PropTypes.number.isRequired,
  setSnackbarOpen: PropTypes.func.isRequired,
  setSnackbar: PropTypes.func.isRequired,
  selectedGroup: PropTypes.string.isRequired,
};
