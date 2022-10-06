# Fastapi Boilerplate

## Installing python packages

From the docker container terminal inside /app.

View available updates:
```bash
pipenv update --outdated
```

Install a package:
```bash
pipenv install <package>
```

Install a dev package:
```bash
pipenv install --dev <package>
```

Update a package:
```bash
pipenv update <package>
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