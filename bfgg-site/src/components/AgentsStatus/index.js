import React from 'react';
import axios from 'axios';
class AgentStatus extends React.Component  {
    constructor(props) {
        super(props);
        this.state = {agents: {}};
    }

    getAgentState() {
        axios.get("http://34.242.147.76:8000/status")
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
            <table>
                <thead>
                    <tr>
                        <th>Agent</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    < AgentRows agents={this.state.agents}/>
                </tbody>
            </table>
            </div>
    );
    }
}

function AgentRows(props) {
    const agents = props.agents;
    console.log(agents)
    if (Object.keys(agents).length > 0) {
        return Object.entries(agents).map(([key, value]) => {
            return <AgentRow key={key} agentIp={key} agentStatus={value}/>
        });

    } else {
        return <tr></tr>
    }
}

function AgentRow(props) {
    const agentIp = props.agentIp;
    const agentStatus = props.agentStatus;
    return (
        <tr>
            <td>{agentIp}</td>
            <td>{agentStatus}</td>
        </tr>
    )
}

export default AgentStatus