import {Box, withStyles} from "@material-ui/core";
import AgentStatus from "../../components/AgentStatus";
import CloneForm from "../../components/CloneForm";
import StartForm from "../../components/StartForm";
import StopForm from "../../components/StopForm";
import React from "react";
import {grey} from "@material-ui/core/colors";
import PropTypes from "prop-types";

const styles = {
    main: {
        marginLeft: "20%"
    }
};
class MainBody extends React.Component {
    render() {
        return <Box padding="2%" className={this.props.classes.main}>
                <AgentStatus />
                <CloneForm />
                <StartForm />
                <StopForm />
            </Box>
    }
}

MainBody.propTypes = {
    classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(MainBody)
