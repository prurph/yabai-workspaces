# Yabai Workspaces

Automate saving and restoring window arrangements on macOS with [koekeishiya/yabai](https://github.com/koekeishiya/yabai).

## Development

This project uses [poetry](https://python-poetry.org).

```sh
# Activate venv
$ poetry shell
```

### API

The api lives in [yabai_workspaces/api](./yabai_workspaces/api/). Run it with the following command from the root directory.

```sh
# Optional log-level to avoid INFO spam every time a route is hit
$ uvicorn yabai_workspaces.api.main:app --reload --log-level warning
```
