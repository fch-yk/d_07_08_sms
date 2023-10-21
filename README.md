# SMS distribution

SMS distribution website. It can send SMS using the [SMSC service](https://smsc.ru/).  
[Quart](https://pypi.org/project/Quart/) is used as an asynchronous web server.  
[Redis](https://hub.docker.com/_/redis) is used to store the history of mailings.

## Installation

### Files and environmental variables

- Download the project files (or clone the project using git);
- Go to the root directory of the project;
- Set up environmental variables in the `.env` file. The variables are:

  - `SMSC_LOGIN` is a login for [SMSC service](https://smsc.ru/) (obligatory);
  - `SMSC_PSW` is a password for [SMSC service](https://smsc.ru/) (obligatory);
  - `SMSC_PHONES` are phones for mailings (separated by commas) (obligatory);
  - `SMSC_VALID` is a valid period of a message (in hours) (obligatory);
  - `SMSC_REDIS_URL` is the Redis base URL (obligatory);
  - `SMSC_REDIS_PASSWORD` is a password for the Redis database (obligatory);
  - `SMSC_BINDING_ADDRESS` is an address to bind the web server to, for example `127.0.0.1:500` (obligatory);
  - `SMSC_DEBUG_MODE` is a boolean that turns on/off debug mode (obligatory). If the value is `True`, messages are not sent;

To set up variables in the `.env` file, create it in the root directory of the project and fill it up like this:

```bash
SMSC_LOGIN=replace_me
SMSC_PSW=replace_me
SMSC_PHONES=+72222222222,+73333333333
SMSC_VALID=1
SMSC_REDIS_URL=redis://default:replace_psw$@replace_hostname:6379/0
SMSC_REDIS_PASSWORD=replace_me
SMSC_BINDING_ADDRESS=127.0.0.1:5000
SMSC_DEBUG_MODE=True
```

### Local installation

- Python 3.10 is required;
- [Docker Desktop](https://docs.docker.com/desktop/) (or [Docker Engine](https://docs.docker.com/engine/install/) and [the Compose plugin](https://docs.docker.com/compose/install/linux/)) should be installed for the Redis database in Docker. This is not obligatory if you prefer to use a local or a cloud Redis version;
- It is recommended to use [venv](https://docs.python.org/3/library/venv.html?highlight=venv#module-venv) for project isolation;
- Set up packages:

```bash
pip install -r requirements.txt
```

Set the `SMSC_BINDING_ADDRESS` variable in the `.env` file:

```bash
SMSC_BINDING_ADDRESS=127.0.0.1:5000
```

Set `localhost` as a hostname for `SMSC_REDIS_URL` in `.env` file:

```bash
SMSC_REDIS_URL=redis://default:replace_psw$@localhost:6379/0
```

Run the Redis database in Docker:

```bash
docker compose -f docker-compose-redis.yaml up -d --build
```

- Start the Quart web server:

```bash
python quart_server.py
```

- Go to the [site](http://127.0.0.1:5000/)

### Docker installation

- [Docker Desktop](https://docs.docker.com/desktop/) (or [Docker Engine](https://docs.docker.com/engine/install/) and [the Compose plugin](https://docs.docker.com/compose/install/linux/)) should be installed;

Set the `SMSC_BINDING_ADDRESS` variable in the `.env` file:

```bash
SMSC_BINDING_ADDRESS=0.0.0.0:5000
```

Set `redis` as a hostname for `SMSC_REDIS_URL` in `.env` file:

```bash
SMSC_REDIS_URL=redis://default:replace_psw$@redis:6379/0
```


Run the services:

```bash
docker compose -f docker-compose.yaml up -d --build
```

- Go to the [site](http://127.0.0.1:5000/)

### Docker installation with debugging in Visual Studio Code

- [Docker Desktop](https://docs.docker.com/desktop/) (or [Docker Engine](https://docs.docker.com/engine/install/) and [the Compose plugin](https://docs.docker.com/compose/install/linux/)) should be installed;

- Set `redis` as a hostname for `SMSC_REDIS_URL` in `.env` file:

```bash
SMSC_REDIS_URL=redis://default:replace_psw$@redis:6379/0
```

- Set `SMSC_BINDING_ADDRESS` in `.env` file:

```bash
SMSC_BINDING_ADDRESS=0.0.0.0:5000
```

- Run the services:

```bash
docker compose -f docker-compose-debug.yaml up -d --build
```

Add a launch configuration to the `.vscode/launch.json` file:

```json
{
  "configurations": [
    {
      "name": "Python: Remote Attach",
      "type": "python",
      "request": "attach",
      "port": 5678,
      "host": "localhost",
      "pathMappings": [
        {
          "localRoot": "${workspaceFolder}",
          "remoteRoot": "/app"
        }
      ]
    }
  ]
}
```

- Choose the "Python: Remote Attach" configuration at the "Run and Debug" tab;
- Press `F5` to start debugging;
- Go to the [site](http://127.0.0.1:5000/);

## Usage

- Go to the [site](http://127.0.0.1:5000/);
- Fill in the message text and start a new mailing by pressing "Send";
- You will see the history of the mailings below the "New mailing" block;

## Project goals

The project was created for educational purposes.
It's a lesson for Python and web developers at [Devman](https://dvmn.org).
