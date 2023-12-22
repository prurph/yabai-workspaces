# Yabai Workspaces

Automate saving and restoring window arrangements on macOS with [koekeishiya/yabai](https://github.com/koekeishiya/yabai).

## Development

### Poetry

This project uses [poetry](https://python-poetry.org)

#### Setup

1. Install [pipx](https://github.com/pypa/pipx)
2. Install [poetry](https://python-poetry.org) with `pipx`
3. Install [pyenv](https://github.com/pyenv/pyenv)
   1. Install python: `pyenv install 3.12`
   2. In the project directory, `pyenv local 3.12`
4. Configure poetry to play nicely with pyenv: `poetry config virtualenvs.prefer-active-python true`

### Management

- Poetry doesn't have a command to upgrade depenencies, instead install [poetry-plugin-up](https://github.com/MousaZeidBaker/poetry-plugin-up)
  - `poetry self add poetry-plugin-up`
  - `poetry up` updates all dependencies and the `pyproject.toml file`
- Can also update with `poetry add package@latest` to install the latest of `package`
- Install dependencies listed in the `pyproject.toml`: `poetry install`

### Activating virtualenvs

#### For use in standalone terminal

```sh
$ poetry shell
```

#### Inside neovim

I recommend **not** running neovim from inside a `poetry shell`. This command spawns a new tty, and so my navigations inside Tmux break because the shell command to determine whether or not the current pane is nvim no longer performs properly. Modifying it to workaround this has drawbacks.

Instead:

- Install pynvim to the virtualenv using poetry: poetry `add --group dev pynvim@latest`
- Launch neovim, then select the appropriate virtualenv with `<leader>cv`. Do this before opening files or restoring a session or the lsp will blow up.
- You may see a warning about Semshi telling you to run `:UpdateRemotePlugins`; do so. Semshi is active if the syntax highlighting does stuff like highlights `self` differently and generally has a lot more color and nuance.

### API

The api lives in [yabai_workspaces/api](./yabai_workspaces/api/). Run it with the following command from the root directory, after `pip install uvicorn` inside of `poetry shell`

```sh
# Optional log-level to avoid INFO spam every time a route is hit
$ uvicorn yabai_workspaces.api.main:app --reload --log-level warning
```
