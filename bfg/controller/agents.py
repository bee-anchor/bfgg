
class Agents:

    def __init__(self):
        self.agents = {}

    @property
    def all_agents(self):
        return self.agents.keys()

    def add_agent(self, agent):
        if agent not in self.agents:
            self.agents[agent] = "Registered"

    def _update_agent_state(self, agent, state):
        if agent not in self.agents:
            print(f"ERROR: agent {agent} hasn't been registered")
        else:
            self.agents[agent] = state

    def update_agent_available(self, agent):
        self._update_agent_state(agent, 'Available')

    def update_agent_busy(self, agent):
        self._update_agent_state(agent, 'Busy')
