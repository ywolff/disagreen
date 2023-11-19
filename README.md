# Climate Debater

> Learn to debate climate change deniers with conversational AI

*Bootstrapped with [Sicarator](https://github.com/sicara/sicarator)*

## Project requirements

### Pyenv and `Python 3.11.6`

- Install [pyenv](https://github.com/pyenv/pyenv) to manage your Python versions and virtual environments:
  ```bash
  curl -sSL https://pyenv.run | bash
  ```
  - If you are on MacOS and experiencing errors on python install with pyenv, follow this [comment](https://github.com/pyenv/pyenv/issues/1740#issuecomment-738749988)
  - Add these lines to your `~/.bashrc` or `~/.zshrc` to be able to activate `pyenv virtualenv`:
      ```bash
      eval "$(pyenv init -)"
      eval "$(pyenv virtualenv-init -)"
      eval "$(pyenv init --path)"
      ```
  - Restart your shell

- Install the right version of `Python` with `pyenv`:
  ```bash
  pyenv install 3.11.6
  ```

### Poetry

- Install [Poetry](https://python-poetry.org) to manage your dependencies and tooling configs:
  ```bash
  curl -sSL https://install.python-poetry.org | python - --version 1.7.0
  ```
  *If you have not previously installed any Python version, you may need to set your global Python version before installing Poetry:*
    ```bash
    pyenv global 3.11.6
    ```

## Installation

### Python virtual environment and dependencies

1. Create a `pyenv` virtual environment and link it to your project folder:
    ```bash
    pyenv virtualenv 3.11.6 climate-debater
    pyenv local climate-debater
    ```
    *Now, every time you are in your project directory your virtualenv will be activated!*


2. Install dependencies with `Poetry`:
    ```bash
    poetry install --no-root
    ```

Steps 1. and 2. can also be done in one command:
```bash
make install
```

### Install git hooks (running before commit and push commands)

```bash
poetry run pre-commit install
```

## Testing

To run unit tests, run `pytest` with:
```bash
pytest tests --cov src
```
or
```bash
make test
```

## Formatting and static analysis

### Code formatting with `ruff`

To check code formatting, run `ruff format` with:
```bash
ruff format --check .
```
or
```bash
make format-check
```

You can also [integrate it to your IDE](https://docs.astral.sh/ruff/integrations/) to reformat
your code each time you save a file.

### Static analysis with `ruff`

To run static analysis, run `ruff` with:
```bash
ruff check src tests
```
or
```bash
make lint-check
```

To run static analysis and to apply auto-fixes, run `ruff` with:
```bash
make lint-fix
```
### Type checking with `mypy`

To type check your code, run `mypy` with:
```bash
mypy src --explicit-package-bases --namespace-packages
```
or
```bash
make type-check
```

## Streamlit

The project includes a Streamlit app.
See its documentation in the [specific README](src/streamlit_app/README.md).
