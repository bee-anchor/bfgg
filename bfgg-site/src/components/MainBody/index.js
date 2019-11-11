import axios from "axios";
import React, {useEffect, useState} from "react";
import PropTypes from 'prop-types';
import { Box } from "@material-ui/core";
import { makeStyles } from '@material-ui/core/styles';
import useInterval from "../../hooks/useInterval";
import AgentStatus from "../../components/AgentStatus";
import CloneForm from "../../components/CloneForm";
import StartForm from "../../components/StartForm";
import StopForm from "../../components/StopForm";
import CustomSnackbar from "../../components/CustomSnackbar";

const useStyles = makeStyles({
    main: {
        marginLeft: "20%"
    }
});

export default function MainBody() {
    const classes = useStyles();
    const [agents, setAgents] = useState({});
    const [snackbarOpen, setSnackbarOpen] = useState(false);
    const [snackbar, setSnackbar] = useState({message: '', type: ''});

    const getAgentState = () => {
        const url = `http://${process.env.REACT_APP_CONTROLLER_HOST}:8000/status`;
        axios.get(url)
            .then((res) => setAgents(res.data))
    };

    useEffect(() => getAgentState(), []);

    useInterval(
        () => getAgentState(),
        5000
    );

    return <Box padding="2%" className={classes.main}>
        <CloneForm setSnackbarOpen={setSnackbarOpen} setSnackbar={setSnackbar}/>
        <StartForm setSnackbarOpen={setSnackbarOpen} setSnackbar={setSnackbar}/>
        <StopForm setSnackbarOpen={setSnackbarOpen} setSnackbar={setSnackbar}/>
        <AgentStatus agents={agents}/>
        <CustomSnackbar setSnackbarOpen={setSnackbarOpen} snackbarOpen={snackbarOpen} message={snackbar.message} type={snackbar.type} />
    </Box>
}

MainBody.propTypes = {
    classes: PropTypes.object.isRequired,
};
