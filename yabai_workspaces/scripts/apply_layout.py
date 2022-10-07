import sys

from pydantic import BaseModel, PositiveInt
from yabai_workspaces.models import Layout
from yabai_workspaces.yabai import Yabai
from yabai_workspaces.layouts.layout_handler import LayoutHandler

import logging


class ApplyLayoutArgs(BaseModel):
    spaces: dict[PositiveInt, Layout]


def main():
    """
    Given a single argument of a JSON string mapping space indexes to layouts, applies the layouts.

    Example:

    $ python yabai_workspaces/scripts/apply_layout.py '
        {
          "spaces": {
            "3": {
              "layout_type": "columns",
              "col_count": 3
            },
            "4": {
              "layout_type": "stack_beside_rows",
              "secondary_row_count": 2,
              "app_stack_priority": [
                "Code"
              ]
            }
          }
        }'
    """
    try:
        args = ApplyLayoutArgs.parse_raw(sys.argv[1])
    except Exception as e:
        raise ValueError(f"Unparseable input json: {sys.argv[1]}") from e

    yabai = Yabai()
    spaces = {space.index: space for space in yabai.spaces()}
    layout_handler = LayoutHandler(yabai)

    for space_idx, layout in args.spaces.items():
        try:
            layout_handler.apply(layout, spaces[space_idx])
        except IndexError:
            logging.warn(f"No space with index {space_idx} found")


if __name__ == "__main__":
    main()
