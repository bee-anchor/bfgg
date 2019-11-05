import React from 'react';
import axios from 'axios';
import PropTypes from 'prop-types';
import { Table, TableHead, TableBody, TableRow, TableCell, Paper } from '@material-ui/core';

class AgentStatus extends React.Component  {
    constructor(props) {
        super(props);
        this.state = {agents: {}};
    }

    getAgentState() {
        axios.get("http://localhost:8000/status")
        .then((res) => this.setState({agents: res.data}))
    }
    
    componentDidMount() {
        this.getAgentState()
        this.timerID = setInterval(
            () => this.getAgentState(),
            5000
        );
    }

    componentWillUnmount() {
    clearInterval(this.timerID);
    }


    render() {
        return (
            <div>
            <Paper>
            <Table aria-label="simple table">
                <TableHead>
                    <TableRow>
                        <TableCell>Agent</TableCell>
                        <TableCell>Status</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    < AgentRows agents={this.state.agents}/>
                </TableBody>
            </Table>
            </Paper>
            </div>
    );
    }
}

function AgentRows(props) {
    const agents = props.agents;
    console.log(agents);
    if (Object.keys(agents).length > 0) {
        return Object.entries(agents).map(([key, value]) => {
            return <AgentRow key={key} agentIp={key} agentStatus={value}/>
        });

    } else {
        return <TableRow></TableRow>
    }
}

AgentRows.propTypes = {
    agents: PropTypes.object,
};

function AgentRow(props) {
    const agentIp = props.agentIp;
    const agentStatus = props.agentStatus;
    return (
        <TableRow>
            <TableCell>{agentIp}</TableCell>
            <TableCell>{agentStatus}</TableCell>
        </TableRow>
    )
}

AgentRow.propTypes = {
    agentIp: PropTypes.string,
    agentStatus: PropTypes.string,
};

export default AgentStatus