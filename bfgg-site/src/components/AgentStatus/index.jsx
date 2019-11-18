import React from 'react';
import PropTypes from 'prop-types';
import {
  Table, TableHead, TableBody, TableRow, TableCell, Card,
} from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles({
  card: {
    marginTop: '40px',
    paddingLeft: '1%',
    paddingRight: '1%',
    paddingBottom: '1%',
  },
});

export default function AgentStatus(props) {
  const classes = useStyles();
  const { agents } = props;

  return (
    <div>
      <Card className={classes.card}>
        <Table aria-label="simple table">
          <TableHead>
            <TableRow>
              <TableCell>Agent</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Cloned repos</TableCell>
              <TableCell>Test running</TableCell>
              <TableCell>Extra information</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            <AgentRows agents={agents} />
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}

AgentStatus.propTypes = {
  agents: PropTypes.objectOf(PropTypes.string).isRequired,
};

function AgentRows(props) {
  const { agents } = props;
  if (Object.keys(agents).length > 0) {
    return Object.entries(agents).map(
      ([key, value]) => <AgentRow key={key} agentIp={key} agentState={value} />,
    );
  }
  return <TableRow />;
}

AgentRows.propTypes = {
  agents: PropTypes.objectOf(PropTypes.string).isRequired,
};

function AgentRow(props) {
  const { agentIp } = props;
  const { agentState } = props;
  return (
    <TableRow>
      <TableCell>{agentIp}</TableCell>
      <TableCell>{agentState['status']}</TableCell>
      <TableCell>{agentState['cloned_repos'].join(", ")}</TableCell>
      <TableCell>{agentState['test_running']}</TableCell>
      <TableCell>{agentState['extra_info']}</TableCell>
    </TableRow>
  );
}

AgentRow.propTypes = {
  agentIp: PropTypes.string.isRequired,
  agentState: PropTypes.object.isRequired,
};
