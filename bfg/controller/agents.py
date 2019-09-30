
class Agents:

    def __init__(self):
        self.agents = {}

    def add_agent(self, agent):
        if agent not in self.agents:
            self.agents[agent] = "Registered"

    def update_agent_state(self, agent, state):
        if agent not in self.agents:
            print(f"ERROR: agent {agent} hasn't been registered")
        else:
            self.agents[agent] = state

    def update_agent_registered(self, agent):
        self.update_agent_state(agent, 'Registered')
