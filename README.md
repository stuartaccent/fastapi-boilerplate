# Fastapi Boilerplate

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
isort .
```

```bash
autoflake --in-place --recursive --remove-unused-variables .
```

## Using the CLI

Several commands have been created to do things like create users.

From the docker container terminal inside /app.

```bash
# to view available commands
python cli.py --help
```

Create a user

```bash
# to view required arguments for create-user
python cli.py create-user --help

# to create the user
python cli.py create-user admin@example.com Admin User password
```
