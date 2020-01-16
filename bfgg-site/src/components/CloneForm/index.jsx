import React, { useState } from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
import {
  Card, Grid, FormControl, TextField, Button,
} from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles({
  button: {
    height: '100%',
  },
  buttonFC: {
    height: '70%',
  },
  card: {
    paddingLeft: '1%',
    paddingRight: '1%',
    paddingBottom: '1%',

  },
});

export default function CloneForm(props) {
  const [repo, setRepo] = useState();
  const { setSnackbarOpen, setSnackbar, selectedGroup } = props;
  const classes = useStyles();

  const sendClone = () => {
    const url = `http://${process.env.REACT_APP_CONTROLLER_HOST}:8000/clone`;
    axios.post(url, {
      repo,
      group: selectedGroup,
    })
      .then(() => {
        setSnackbar({ message: 'Clone requested', type: 'success' });
        setSnackbarOpen(true);
      },
      () => {
        setSnackbar({ message: 'Clone failed', type: 'error' });
        setSnackbarOpen(true);
      });
  };

  return (
    <Card className={classes.card}>
      <Grid container spacing={3}>
        <Grid item xs={9}>
          <TextField
            id="clone-repo-url"
            label="clone repo url"
            placeholder="git@bitbucket.org:company/repo.git"
            fullWidth
            margin="normal"
            variant="outlined"
            onChange={(e) => setRepo(e.target.value)}
          />
        </Grid>
        <Grid item xs>
          <FormControl fullWidth margin="normal" className={classes.buttonFC}>
            <Button
              fullWidth
              variant="contained"
              color="primary"
              onClick={sendClone}
              className={classes.button}
            >
                            Clone
            </Button>
          </FormControl>
        </Grid>
      </Grid>
    </Card>
  );
}

CloneForm.propTypes = {
  setSnackbarOpen: PropTypes.func.isRequired,
  setSnackbar: PropTypes.func.isRequired,
  selectedGroup: PropTypes.string.isRequired,
};
