# Fastapi Boilerplate

## Running

Using docker compose:
```bash
docker compose up
```

## Installing python packages

From the docker container terminal inside /app.

Install a package:
```bash
poetry add <package>
```

Install a dev package:
```bash
poetry add --dev <package>
```

Update all package:
```bash
poetry update
```

Update one or more package:
```bash
poetry update <package>
```

Show package dependency tree:
```bash
poetry show --tree
```

## Running tests

From the docker container terminal inside /app.

```bash
pytest --asyncio-mode=auto
```

## Auto Code Linting

From the docker container terminal inside /app.

```bash
black .
```

```bash
ruff --fix .
```

## Using the CLI

Several commands have been created to do things like create users.

From the docker container terminal inside /app.

```bash
# to view available commands
python cli.py --help
```
