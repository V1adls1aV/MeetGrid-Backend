# MeetGrid backend

## Quickstart

Ensure docker daemon and running. For backend to start on localhost, run the following:

```sh
docker compose up
```

After that, you can use the meet-grid app on [http://localhost:5173](http://localhost:5173) (ensure that frontend is running).

## Development guide

### 1. Dependencies & Virtual environment

#### a. Install [uv](https://docs.astral.sh/uv/)

You can install it via `curl` or `brew`:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```sh
brew install uv
```

Now, sync all python dependencies:

```sh
uv sync --all-extras
```

### 2. Configure project

Application has 2 types of configs:
- public  – `config.yaml` (For simple launch – do not change anything)
- private – `.env` <- remember to **copy** content of `.env.example` here


### 3. Launch application

To launch app out of the box, run the following: (ensure docker daemon is running)

```sh
uv run app.py run --init-env
```

Make sure you have testcontainers installed, `--init-env` will automatically launch `redis` test container (it is used primarily for tests, but for local-host it is fine too).

```sh
uv run app.py test --verbose
```

```sh
uv run app.py --help  # this works well to :)
```
