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
* Twisted - for running the flask app

The Controller and Agents have three main parts that comprises their inter-communication:

```
       Controller                                      Agent

+-----------------------+                    +--------------------------+
|                       |                    |                          |
|                       |                    |                          |
|  Agent State Poller   +<-------------------+       State Sender       |
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


+-----------------------+                    +--------------------------+
|                       |  Request results   |                          |
|                       +------------------->+                          |
|     Results Getter    |                    |       Results Sender     |
|                       |                    |          (thread)        |
|                       +<-------------------+                          |
|                       |    Send results    |                          |
+-----------------------+                    +--------------------------+
```

The controller's 'Agent State Poller' sits listening for messages from the agents informing it
of their current status. When it sees a new one it adds it to it's list of agents it currently knows about.
It expects to hear from them every few seconds or will consider the agent 'dead'.
Along side this the agents run a 'Task Handler' that sits listening for commands from the controller. When a task is scheduled from the API or UI,
the controller sends a message to all connected agents in the correct state to perform the task, knowing when it is done via a status change from the 'Agent State Poller'.
There is an additional thread that runs on the agent for sending results to the controller. The controller will request the last results from each
agent on demand and then push them up to S3. 


Additionally there is an API that runs alongside this on the controller for sending tasks and getting cluster status.
There will also be a react front end eventually driven by the APIs.

## Running BFGG

### Configuration

There is a .env file in the project where required config values are defined.
These can be overridden by environment variables, and some will need to be overridden when deploying a cluster.

### Prereqs

* Python >=3.7
* Java 8
* Git
* Gatling (https://gatling.io/open-source - download and unzip somewhere)

### Setup

* Create a virtual env: `python3 -m venv venv`
* Get into the virtual env: `source venv/bin/activate`
* Install required libraries: `pip install -r requirements.txt`

#### Run the Controller:

`PYTHONPATH=~/projects/bfgg LOG_LEVEL=DEBUG twistd -n web --wsgi run_controller.app --port tcp:8000`

#### Run the Agents:

`RESULTS_FOLDER=<location/to/save/results>  GATLING_LOCATION=<location/of/gatling.sh> TESTS_LOCATION=<location/of/gatling/tests> LOG_LEVEL=DEBUG python run_agent.py`

## APIs

Get the status of all connected agents
```
GET /status
```

Clone the repo containing the Gatling test code
```
POST /clone

{
    "repo": "repoUrl"
}
```

Instruct all agents to start the test specified. Can optionally send additional java opts for configuring the
java process and setting parameters for a test.
```
POST /start

{
	"project": "project",
	"testClass": "testClassToRun",
	"javaOpts": "-Xmx14G -DTEST=hello"
}
```
Once a test has run on the agents, get the Gatling results from that run
```
GET /results
```

## Unit Tests

To run the bfgg python unit tests: `pytest test/`


