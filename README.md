# Fastapi Boilerplate

## Running

Using docker compose:
```bash
docker compose up --watch
```

## Python Packages

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

## Auto Code Linting

```bash
./run.sh uv run black .
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
