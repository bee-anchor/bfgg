import {Snackbar, SnackbarContent, IconButton} from '@material-ui/core';
import React from "react";
import { amber, green, red, blue } from '@material-ui/core/colors';
import CheckCircleIcon from '@material-ui/icons/CheckCircle';
import WarningIcon from '@material-ui/icons/Warning';
import ErrorIcon from '@material-ui/icons/Error';
import InfoIcon from '@material-ui/icons/Info';
import CloseIcon from '@material-ui/icons/Close';
import PropTypes from 'prop-types';
import { makeStyles } from '@material-ui/core/styles';

const variantIcon = {
    success: CheckCircleIcon,
    warning: WarningIcon,
    error: ErrorIcon,
    info: InfoIcon,
};
const useStyles = makeStyles({
    success: {
        backgroundColor: green[600],
    },
    error: {
        backgroundColor: red[600],
    },
    info: {
        backgroundColor: blue[600],
    },
    warning: {
        backgroundColor: amber[600],
    },
    icon: {
        fontSize: 20,
    },
    iconVariant: {
        opacity: 0.9,
        marginRight: '2px'
    },
    message: {
        display: 'flex',
        alignItems: 'center',
    },
});

export default function CustomSnackbar(props) {
    const classes = useStyles();
    const { setSnackbarOpen, snackbarOpen, message, type} = props;
    const Icon = variantIcon[type];
    console.log({ setSnackbarOpen, snackbarOpen, message, type});

    const handleSnackClose = () => {
        setSnackbarOpen(false);
    };
    return <Snackbar
        anchorOrigin={{
            vertical: 'top',
            horizontal: 'right',
        }}
        open={snackbarOpen}
        autoHideDuration={10000}
        onClose={handleSnackClose}
    >
        <SnackbarContent
            className={classes[type]}
            message={
                <span id="client-snackbar" className={classes.message}>
                    <Icon className={`${classes.icon} ${classes.iconVariant}`}/>
                    {message}
                </span>
            }
            action={[
                    <IconButton key="close" aria-label="close" color="inherit" onClick={handleSnackClose}>
                    <CloseIcon className={classes.icon} />
                    </IconButton>
            ]}
        />
    </Snackbar>
}

CustomSnackbar.propTypes = {
    setSnackbarOpen: PropTypes.func,
    snackbarOpen: PropTypes.bool,
    message: PropTypes.string,
    type: PropTypes.string,
};

