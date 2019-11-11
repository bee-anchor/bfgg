import React, { useState } from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
import { Card, Grid, FormControl, TextField, Button } from '@material-ui/core';
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

    }
});

export default function CloneForm(props) {
    const [url, setUrl] = useState();
    const { setSnackbarOpen, setSnackbar } = props;
    const classes = useStyles();

    const sendClone = () => {
        axios.post("http://localhost:8000/clone", {
            "repo": url
        })
        .then(() => {
                setSnackbar({message: 'Clone requested', type: 'success'});
                setSnackbarOpen(true)
            },
            () => {
                setSnackbar({message: 'Clone failed', type: 'error'});
                setSnackbarOpen(true)
            }
        )
    };

    return (
        <Card className={classes.card}>
            <Grid container spacing={3}>
            <Grid item xs={9}>
                <TextField
                    id="clone-repo-url"
                    label="clone repo url"
                    fullWidth
                    margin="normal"
                    variant="outlined"
                    onChange={e => setUrl(e.target.value)}
                />
            </Grid>
            <Grid item xs>
            <FormControl fullWidth margin='normal' className={classes.buttonFC}>
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
    setSnackbarOpen: PropTypes.func,
    setSnackbar: PropTypes.func,
};