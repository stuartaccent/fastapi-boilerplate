# Fastapi Boilerplate

## Running

Using docker compose:
```bash
docker compose up --watch
```

## Python packages

install:
```bash
./run.sh uv add <package==1.0.0>
```

remove:
```bash
./run.sh uv remove <package>
```

## Running tests

```bash
./run.sh uv run pytest
```

## Code linting

```bash
./run.sh uv run ruff format .
```

```bash
./run.sh uv run ruff check --fix .
```

## Using the CLI

Several commands have been created to do things like create users.
```bash
# to view available commands
./run.sh uv run app/cli.py --help
```
