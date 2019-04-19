#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import subprocess
import sys
from typing import Tuple, Callable, Generator


def get_workspaces() -> dict:
    with open(os.devnull) as devnull:
        p = subprocess.Popen(["swaymsg", "-r", "-t", "get_workspaces"], stdout=subprocess.PIPE, stderr=devnull)
        j = json.load(p.stdout)
        p.wait()

    return j


def raises(fn: Callable, *args, **kwargs) -> bool:
    # noinspection PyBroadException
    try:
        fn(*args, **kwargs)
        return False
    except Exception:
        return True


# noinspection PyShadowingNames
def iter_renames_to_do(workspaces: dict) -> Generator[Tuple, None, None]:
    workspace_names = \
        map(
            lambda name: int(name),
            sorted(
                filter(
                    lambda name: not raises(int, name),
                    map(
                        lambda workspace: workspace["name"],
                        workspaces
                    )
                )
            )
        )

    count = 1
    for name in workspace_names:
        if name != count:
            yield str(name), str(count)

        count += 1


def rename_workspace(old: str, new: str):
    with open(os.devnull) as devnull:
        p = subprocess.Popen(["swaymsg", "rename", "workspace", old, "to", new], stdout=devnull, stderr=devnull)
        p.wait()


def main():
    workspaces = get_workspaces()

    for rename_op in iter_renames_to_do(workspaces):
        rename_workspace(*rename_op)


if __name__ == '__main__':
    main()
