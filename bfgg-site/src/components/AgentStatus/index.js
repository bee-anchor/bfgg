import React  from 'react';
import PropTypes from 'prop-types';
import {Table, TableHead, TableBody, TableRow, TableCell, Card} from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles({
    card: {
        marginTop: '40px',
        paddingLeft: '1%',
        paddingRight: '1%',
        paddingBottom: '1%',
    }
});

export default function AgentStatus(props)  {
    const classes = useStyles();

    return (
        <div>
        <Card className={classes.card}>
        <Table aria-label="simple table">
            <TableHead>
                <TableRow>
                    <TableCell>Agent</TableCell>
                    <TableCell>Status</TableCell>
                </TableRow>
            </TableHead>
            <TableBody>
                < AgentRows agents={props.agents}/>
            </TableBody>
        </Table>
        </Card>
        </div>
    );
}

AgentStatus.propTypes = {
    agents: PropTypes.object,
};

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