import React, { useState } from 'react';
import axios from 'axios';
import { Card, TextField, Button } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import PropTypes from 'prop-types';

const useStyles = makeStyles({
  card: {
    marginTop: '40px',
    paddingLeft: '1%',
    paddingRight: '1%',
    paddingBottom: '1%',
  },
  button: {
    marginTop: '1%',
  },
});

export default function StartForm(props) {
  const classes = useStyles();
  const { setSnackbarOpen, setSnackbar, selectedGroup } = props;
  const [name, setName] = useState();
  const [test, setTest] = useState();
  const [javaOpts, setJavaOpts] = useState();

  const sendStart = () => {
    const url = `http://${process.env.REACT_APP_CONTROLLER_HOST}:8000/start`;
    axios.post(url, {
      group: selectedGroup,
      project: name,
      testClass: test,
      javaOpts,
    }, {validateStatus: (status) => status === 200 })
    .then(() => {
      setSnackbar({ message: 'Start test requested', type: 'success' });
      setSnackbarOpen(true);
    })
    .catch((error) => {
      if (error.response) {
        setSnackbar({ message: error.response.data.error, type: 'error' });
        setSnackbarOpen(true);
      } else if (error.request) {
        setSnackbar({ message: "Something went wrong", type: 'error' });
        setSnackbarOpen(true);
        console.log(error.request);
        console.log(error.message);
      } else {
        setSnackbar({ message: "Something went wrong", type: 'error' });
        setSnackbarOpen(true);
        console.log(error.message);
      }
    });
  };

  return (
    <Card className={classes.card}>
      <form noValidate autoComplete="off">
        <TextField
          id="project-name"
          label="Project"
          placeholder="repo_name"
          helperText="The name of the repo containing the tests"
          fullWidth
          margin="normal"
          variant="filled"
          onChange={(e) => setName(e.target.value)}
        />
        <TextField
          id="test-class"
          label="Test Class"
          placeholder="TestClass"
          helperText="The test class to be run"
          fullWidth
          margin="normal"
          variant="filled"
          onChange={(e) => setTest(e.target.value)}
        />
        <TextField
          id="java-opts"
          label="JavaOpts"
          placeholder="-Xmx14G -DUSERS=33 -DDURATION=10minutes"
          helperText="Additional javaOpts to be passed to the test"
          fullWidth
          margin="normal"
          variant="filled"
          onChange={(e) => setJavaOpts(e.target.value)}
        />
        <Button
          fullWidth
          variant="contained"
          color="primary"
          size="large"
          className={classes.button}
          onClick={sendStart}
        >
                    Start Test
        </Button>
      </form>
    </Card>
  );
}

StartForm.propTypes = {
  setSnackbarOpen: PropTypes.func.isRequired,
  setSnackbar: PropTypes.func.isRequired,
  selectedGroup: PropTypes.string.isRequired,
};
