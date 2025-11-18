# MeetGrid backend

## Get started

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
- public  – `config.yaml`
- private – `.env` <- copy `.env.example` here


### 3. Launch application

To launch app out of the box, run the following:

```sh
uv run app.py run --init-env
```

Make sure you have testcontainers installed, `--init-env` will automatically launch `redis` test container (it is used primarily for tests).

```sh
uv run app.py test --verbose
```

```sh
uv run app.py --help  # this works well to :)
```
