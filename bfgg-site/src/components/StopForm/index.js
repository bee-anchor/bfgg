import React from 'react';
import axios from 'axios';
import { Card, Button } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import PropTypes from "prop-types";
import CloneForm from "../CloneForm";

const useStyles = makeStyles({
    card: {
        marginTop: '40px',
        paddingTop: '1%',
        paddingLeft: '1%',
        paddingRight: '1%',
        paddingBottom: '1%',
    },
});

export default function StopForm(props)  {
    const classes = useStyles();
    const { setSnackbarOpen, setSnackbar } = props;

    const sendStop = () => {
        axios.post("http://localhost:8000/stop")
        .then(() => {
                setSnackbar({message: 'Stop requested', type: 'success'});
                setSnackbarOpen(true)
            },
            () => {
                setSnackbar({message: 'Failed to stop test', type: 'error'});
                setSnackbarOpen(true)
            })
    };
    
    return (
        <Card className={classes.card}>
        <form noValidate autoComplete="off">
            <Button
                    fullWidth
                    variant="contained"
                    color="secondary"
                    onClick={sendStop}
                    size='large'
                >
                    Stop Test
                </Button>
        </form>
        </Card>
    );
}

StopForm.propTypes = {
    setSnackbarOpen: PropTypes.func,
    setSnackbar: PropTypes.func,
};