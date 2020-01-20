# BFG-G
#### Big F***ing/Friendly Gatling Gun

Tool to both run Gatling tests in a distributed manner,
and provide a web UI to view and manage test runs.

Composed of two parts: the Controller and Agents

### The Controller

This runs on a single machine, and coordinates the 'agents'. It also runs the web UI and API for users to start, stop and monitor tests

### The Agents

This runs on one of more machines, checks in with the 'controller' and waits for instructions.
The agents are where the Gatling tests are actually run.

## Architecture

The language used is Python, with a web UI in React

Key technologies used:
* ZeroMQ - https://zeromq.org/
* Flask - https://flask.palletsprojects.com/
* React - https://reactjs.org/

```
+-------------------------------------------+    +------------------------------------------+
|                                           |    |                                          |
|                                           |    |                                          |
|                Controller                 |    |                   Agent                  |
|                                           |    |                                          |
|                                           |    |                                          |
|  +-----------------+      +-------------+ |    | +------------+      +----------------+   |
|  |                 <------+   Incoming  | |    | |  Outgoing  <------+                |   |
|  | Metrics handler |      |   message   | |    | |  message   |      | Status handler |   |
|  |                 |      |   handler   <--------+  handler   |      |    (thread)    |   |
|  +-----------------+      |   (thread)  | |    | |  (thread)  |      +-----^----------+   |
|                           +-+--+--------+ |    | +----^----^--+            |              |
|  +----------------+               |  |    |    |      |    |               |              |
|  |                |               |  |    |    |      |    ----------------+------------+ |
|  | Report handler <---------------+  |    |    |      -----------------+                | |
|  |                |                  |    |    |                       |                | |
|  +----------------+                  |    |    |                       |                | |
|                                      |    |    |                     +-+--------------+ | |
|  +----------------+                  |    |    |                     |  Log follower  | | |
|  |                <------------------+    |    |                     +--------^-------+ | |
|  |     State      |                       |    |                     +--------|-------+ | |
|  |                |       +-------------+ |    | +-------------+     |                +-+ |
|  +-------------+--+       |   Outgoing  | |    | |  Incoming   |     | Gatling runner |   |
|                |          |   message   | |    | |  message    +----->                |   |
|                |    +----->   handler   +-------->  handler    |     +----------------+   |
|                |    |     |   (thread)  | |    | |  (thread)   |                          |
|                |    |     +-------------+ |    | +-------------+                          |
|                |    |                     |    |                                          |
|                |    |                     |    |                                          |
|                |    |                     |    +------------------------------------------+
|              +-v----+--------+            |
|              |               |            |
|              |      API      |            |
|              |               |            |
|              +--------+------+            |
|                       |                   |
|                       |                   |
|              +--------v--------+          |
|              |                 |          |
|              |  React Web App  |          |
|              |                 |          |
|              +-----------------+          |
|                                           |
|                                           |
+-------------------------------------------+
```

#### And example flow - running a test:
1. An agent comes online - it's status handler starts in a thread and triggers and outgoing message to the controller with it's status. This 'registers' the agent with the controller.
1. The agent's status handler will continue to trigger status massages on a regular interval, so the controller knows the agent is still alive.
1. A user of the React web app, triggers a test to be started.
1. The web app sends the request to the API.
1. The API triggers an outgoing message to the agent(s) to start the specified test. It also creates an item in DynamoDB with the test details and start time.
1. The agent receives the message and starts a new gatling runner.
1. The gatling runner starts the gatling process to run the test, and starts a log follower to send gatling test logs to the controller.
1. The gatling runner updates the agents internal status to say the test is running.
1. The status handler triggers a message to update the controller with it's latest status.
1. The controller receives the status message and updates it's internal state.
1. This new state will be reflected in the web app when it next polls the status API endpoint.
1. While the test is running, logs received from the agents are saved by the controller, and also used to generate metrics for the /metrics API endpoint - this is intended to be scraped by a Prometheus instance.
1. Once the test finishes, the gatling runner updates the agent internal status, and then terminates along with the log follower.
1. When the controller receives the test finished status update (and all other agents have already finished the test too) the controller starts the report handler to generate the gatling report, and upload it to s3.
1. The controller then also updates the test in DynamoDB with it's end time and results url.


## Running BFGG

### Configuration

There is a .env file in the project where required config values are defined.
These can be overridden by environment variables, and some will need to be overridden when deploying a cluster.
##### Key environment variables that should be changed when deploying a cluster:

* CONTROLLER_HOST - only used by agents - set to the IP of the controller
* AGENT_MESSAGING_PORT - only change if desired
* CONTROLLER_MESSAGING_PORT - only change if desired
* TESTS_LOCATION - only used by agents - set to an absolute path to store test files
* RESULTS_FOLDER - set to an absolute path to store results
* GATLING_LOCATION - set to absolute path where gatling.sh file is located
* S3_BUCKET - set to name of bucket to store reports
* DYNAMODB_TABLE - set to name of table to store test details

### Prereqs

* Python >=3.7
* Java 8
* Git
* Gatling (https://gatling.io/open-source - download and unzip somewhere)
* Node.js

### Backend Setup

* Create a virtual env: `python3 -m venv venv`
* Get into the virtual env: `source venv/bin/activate`
* Install required libraries: `pip install -r requirements.txt`

#### Run the Controller:

`PYTHONPATH=~/projects/bfgg LOG_LEVEL=DEBUG twistd -n web --wsgi run_controller.app --port tcp:8000`

#### Run the Agents:

`RESULTS_FOLDER=<location/to/save/results>  GATLING_LOCATION=<location/of/gatling.sh> TESTS_LOCATION=<location/of/gatling/tests> LOG_LEVEL=DEBUG python run_agent.py`

### React frontend setup:

Install and run frontend for development:
```
cd bfgg-site
npm install
npm start
```

## APIs

> Note: The default group that agents come online with is 'ungrouped' 

Get the status of all connected agents
```
GET /status
```

Group the specified agents into a new named group:

```
POST /group

{
    "group": "group",
    "agents": ["ip1", "ip2", ...]
}
```

Specified group clone the repo containing the Gatling test code:
```
POST /clone

{
    "group": "group",
    "repo": "repoUrl"
}
```

Specified group start the test specified:

(Can optionally send additional java opts for configuring the
java process and setting parameters for a test)
```
POST /start

{
    "group": "group",
	"project": "project",
	"testClass": "testClassToRun",
	"javaOpts": "-Xmx14G -DTEST=hello"
}
```
Specified group stop running test:

```
POST /stop

{
    "group": "group",
}
```

Get current test entries in the DynamoDB table:

```
GET /past-tests

```

Re-generate report for the last test run by the specified group (should never need to be used):

```
POST /results

{
    "group": "group"
}
```

## Test and Lint

`make run_tests` - run bfgg unit tests
`make lint` - lint the python code
`cd bfgg-site && npx eslint --ext .jsx .` - lint the React site code


