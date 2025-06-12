
# Heroku MCP Code Execution - Python

- [Heroku MCP Code Execution - Python](#heroku-mcp-code-execution---python)
  - [Automatic Deployment](#automatic-deployment)
  - [Manual Deployment](#manual-deployment)
    - [**Set Required Environment Variables from Heroku CLI**](#set-required-environment-variables-from-heroku-cli)
  - [Local Testing](#local-testing)
    - [Local Streamable HTTP, SSE](#local-streamable-http-sse)
      - [Local Streamable HTTP, SSE - Example Requests](#local-streamable-http-sse---example-requests)
    - [Local STDIO](#local-stdio)
      - [1. Local STDIO - Example Python STDIO Client](#1-local-stdio---example-python-stdio-client)
      - [2. Local STDIO - Direct Calls](#2-local-stdio---direct-calls)
  - [Remote Testing](#remote-testing)
    - [Remote Streamable HTTP, SSE](#remote-streamable-http-sse)
    - [Remote STDIO](#remote-stdio)
      - [1. Remote STDIO - Example Python STDIO Client, Running On-Server](#1-remote-stdio---example-python-stdio-client-running-on-server)
      - [2. Remote STDIO - Direct Calls to One-Off Dyno](#2-remote-stdio---direct-calls-to-one-off-dyno)
    - [3. Coming Soon - Heroku MCP Gateway!](#3-coming-soon---heroku-mcp-gateway)

## Automatic Deployment

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://www.heroku.com/deploy?template=https://github.com/heroku/mcp-code-exec-python)

## Manual Deployment
### **Set Required Environment Variables from Heroku CLI**
Instead of manually setting each variable, use the Heroku CLI to pull the correct values.

```bash
export APP_NAME=<your-heroku-app-name>
heroku create $APP_NAME

heroku buildpacks:set heroku/python -a $APP_NAME

# set a private API key that you create, for example:
heroku config:set API_KEY=$(openssl rand -hex 32) -a $APP_NAME
heroku config:set STDIO_MODE_ONLY=<true/false> -a $APP_NAME
# set the remote server type (module) that your web process will use (only relevant for web deployments)
heroku config:set REMOTE_SERVER_TRANSPORT_MODULE=<streamable_http_server/sse_server>
```
*Note: we recommend setting `STDIO_MODE_ONLY` to `true` for security and code execution isolation security in non-dev environments.*

If you *only* want local & deployed `STDIO` capabilities (no `SSE server`), run:
```bash
heroku ps:scale web=0 -a $APP_NAME
```
If you do want a deployed `SSE` server, run:
```bash
heroku ps:scale web=1 -a $APP_NAME
heroku config:set WEB_CONCURRENCY=1 -a $APP_NAME
```

Optionally, put these config variables into a local .env file for local development:
```bash
heroku config -a $APP_NAME --shell | tee .env > /dev/null
```

Next, connect your app to your git repo:
```bash
heroku git:remote -a $APP_NAME
```
And deploy!
```bash
git push heroku main
```
View logs with:
```bash
heroku logs --tail -a $APP_NAME
```

## Local Testing
One-time packages installation:
```bash
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Local Streamable HTTP, SSE
If you're testing (stateless) Streamable HTTP OR SSE, in one terminal pane you'll need to start the server:
```bash
source venv/bin/activate
export API_KEY=$(heroku config:get API_KEY -a $APP_NAME)
# Either run src.streamable_http_server or src.sse_server, here:
uvicorn src.streamable_http_server:app --reload
```
*Running with `--reload` is optional, but great for local development*

Next, in a new pane, you can try running some queries against your server:

#### Local Streamable HTTP, SSE - Example Requests
First run:
```bash
export API_KEY=$(heroku config:get API_KEY -a $APP_NAME)
```

In the following commands, use either `example_clients/streamable_http_client.py` if you ran the streamable HTTP server above, or `example_clients/sse_client.py` if you're running the SSE server.

List tools:
```bash
python example_clients/streamable_http_client.py mcp list_tools | jq
```

Example tool call request:
*NOTE: this will intentionally NOT work if you have set `STDIO_MODE_ONLY` to `true`.*
```bash
python example_clients/streamable_http_client.py mcp call_tool --args '{
  "name": "code_exec_python",
  "arguments": {
    "code": "import numpy as np; print(np.random.rand(50).tolist())",
    "packages": ["numpy"]
  }
}' | jq
```

### Local STDIO
There are two ways to easily test out your MCP server in STDIO mode:

#### 1. Local STDIO - Example Python STDIO Client
List tools:
```bash
python example_clients/stdio_client.py mcp list_tools | jq
```

Example tool call request:
```bash
python example_clients/stdio_client.py mcp call_tool --args '{
  "name": "code_exec_python",
  "arguments": {
    "code": "import numpy as np; print(np.random.rand(50).tolist())",
    "packages": ["numpy"]
  }
}' | jq
```

#### 2. Local STDIO - Direct Calls
Example tool call request:
```bash
cat <<EOF | python -m src.stdio_server

{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"0.1.0","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}

{"jsonrpc":"2.0","method":"notifications/initialized","params":{}}

{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"code_exec_python","arguments":{"code":"import numpy as np; print(np.random.rand(50).tolist())","packages":["numpy"]}}}
EOF
```
*(Note that the server expects the client to send a shutdown request, so you can stop the connection with CTRL-C)*

## Remote Testing

### Remote Streamable HTTP, SSE
To test your remote `Streamble HTTP` or `SSE` server, you'll need to make sure a web process is actually spun up. To save on costs, by default this repository doesn't spin up web dynos on creation, as many folks only want to use `STDIO` mode (local and one-off dyno) requests:
```bash
heroku ps:scale web=1 -a $APP_NAME
```
You only need to do this once, unless you spin back down to 0 web dynos to save on costs (`heroku ps:scale web=0 -a $APP_NAME`). To confirm currently running dynos, use `heroku ps -a $APP_NAME`.

By default, this app deploys a Streamable HTTP MCP server - if you want to deploy an SSE server, run:
```bash
heroku config:set REMOTE_SERVER_TRANSPORT_MODULE=sse_server
```
Which will affect which server is run in the Procfile.

Next, run:

```bash
export API_KEY=$(heroku config:get API_KEY -a $APP_NAME)
export MCP_SERVER_URL=$(heroku info -s -a $APP_NAME | grep web_url | cut -d= -f2)
```

Next, you can run the same queries as shown in the [Local SSE - Example Requests](#local-streamable-http-sse---example-requests) testing section - because you've set `MCP_SERVER_URL`, the client will call out to your deployed server.

### Remote STDIO
There are two ways to test out your remote MCP server in STDIO mode:

#### 1. Remote STDIO - Example Python STDIO Client, Running On-Server
To run against your deployed code, you can run the example client code on your deployed server inside a one-off dyno:
```bash
heroku run --app $APP_NAME -- bash -c 'python -m example_clients.stdio_client mcp list_tools | jq'
```
or:
```bash
heroku run --app $APP_NAME -- bash -c '
python -m example_clients.stdio_client mcp call_tool --args '\''{
  "name": "code_exec_python",
  "arguments": {
    "code": "import numpy as np; print(np.random.rand(50).tolist())",
    "packages": ["numpy"]
  }
}'\'' | jq
'
```

#### 2. Remote STDIO - Direct Calls to One-Off Dyno
Or, you can also run or simulate a client locally that sends your client-side requests to a one-off dyno:

```bash
heroku run --app "$APP_NAME" -- bash -c "python -m src.stdio_server 2> logs.txt" <<EOF

{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"0.1.0","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}

{"jsonrpc":"2.0","method":"notifications/initialized","params":{}}

{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"code_exec_python","arguments":{"code":"import numpy as np; print(np.random.rand(50).tolist())","packages":["numpy"]}}}
EOF
```

Again, note that since we're running our request through a single command, we're unable to simulate a client's shutdown request.

### 3. Coming Soon - Heroku MCP Gateway!
Soon, you'll also be able to connect up your MCP repo to Heroku's MCP Gateway, which will make streaming requests and responses from one-off MCP dynos simple!

The Heroku MCP Gateway implements a rendezvous protocol so that you can easily talk to your MCP server one-off dynos (code execution isolation!) with seamless back-and-forth communication.

After [deploying and registering](https://devcenter.heroku.com/articles/heroku-inference-working-with-mcp) your MCP app on heroku, requests made to Heroku's [`v1/mcp/servers`](https://devcenter.heroku.com/articles/heroku-inference-api-v1-mcp-servers) will show you your registered MCP tools, and requests made to [`v1/agents/heroku`](https://devcenter.heroku.com/articles/heroku-inference-api-v1-agents-heroku) will be able to execute your MCP tools automatically via one-off dynos.
