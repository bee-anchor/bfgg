# BFG-G
#### Big F***ing/Friendly Gatling Gun

Tool to both run Gatling tests in a distributed manner,
and provide a web UI to view and manage test runs.

Composed of two parts: the Controller and Agents

### The Controller

This runs on a single machine, and coordinates the 'agents'. It also runs the web UI and API for users to start, stop and monitor tests

### The Agents

This runs on one of more machines, registers the machine with the 'controller' and waits for instructions from the 'controller'.
The agents is where the Gatling tests are actually run.

## Architecture

The language used is Python, with a web UI in React
Libraries used are:
* ZeroMQ - a messaging library used for communication between controller and agents
* Flask - web framework used for the API
* threading - standard library for parallelism using threads
* subprocess - standard library for starting other processes - used for git processes and running Gatling

The Controller and Agents have three main parts that comprises their inter-communication:

```
       Controller                                      Agent

+-----------------------+                    +--------------------------+
|                       |      Register      |                          |
|                       +<-------------------+                          |
|      Registrator      |                    |       Registration       |
|       (thread)        |                    |                          |
|                       +------------------->+                          |
|                       |    Acknowledge     |                          |
+-----------------------+                    +--------------------------+

+-----------------------+                    +--------------------------+
|                       |                    |                          |
|                       |                    |                          |
|  Agent State Puller   +<-------------------+       State Sender       |
|       (thread)        |   Current State    |        (thread)          |
|                       |                    |                          |
|                       |                    |                          |
+-----------------------+                    +--------------------------+

+-----------------------+                    +--------------------------+
|                       |                    |                          |
|                       |                    |                          |
|      Task Pusher      +------------------->+       Task Handler       |
|       (thread)        |  Task to execute   |         (thread)         |
|                       |                    |                          |
|                       |                    |                          |
+-----------------------+                    +--------------------------+

```

The controller has a registrator thread that always runs, waiting for new agents to join the cluster.
After an agent has registered with the controller, the controller's 'Agent State Puller' sits listening for messages from the agents informing it
of their current status. It expects to hear from them every few seconds or will consider the agent 'dead'.
Along side this the agents run a 'Task Handler' that sits listening for commands from the controller. When a task is scheduled from the API or UI,
the controller sends a message to all connected agents in the correct state to perform the task, knowing when it is done via a status change from the 'Agent State Puller'


## Running BFGG

### Configuration

There is a .env file in the project where required config values are defined.
These can be overridden by environment variables, and generally only the CONTROLLER_HOST will need to be overridden when deploying a cluster.

### The Controller:

Prereqs are:
* Python 3
* requirements.txt libraries

Run with:

`gunicorn -b 0.0.0.0:<port> wsgi`


### The Agents

Prereqs are:
* Python 3
* Java 8
* SBT (scala build tool)
* Git
* requirements.txt libraries

Run with:

`python run_agent.py`


