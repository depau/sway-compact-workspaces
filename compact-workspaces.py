#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import subprocess

from typing import Tuple, Callable, Generator, Any


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


def lists_join(*lists: list) -> Generator[Any, None, None]:
    for l in lists:
        for i in l:
            yield i

# noinspection PyShadowingNames
def iter_renames_to_do(workspaces: list) -> Generator[Tuple, None, None]:
    output_workspaces = {}
    for workspace in workspaces:
        name = workspace["name"]
        output = workspace["output"]

        if raises(int, name):
            continue
        if output not in output_workspaces:
            output_workspaces[output] = []

        output_workspaces[output].append(int(name))

    all_workspaces = set(lists_join(*output_workspaces.values()))
    abs_min = min(all_workspaces)

    for output in reversed(sorted(output_workspaces.keys(), key=lambda output: min(output_workspaces[output]))):
        output_wsset = set(output_workspaces[output])
        others = all_workspaces - output_wsset

        lowest = min(output_wsset)
        highest = max(output_wsset)

        # Make output with lowest workspace start with workspace 1
        if lowest == abs_min:
            base = 1
        else:
            base = lowest
        counter = base

        for name in sorted(output_wsset):
            if name != counter:
                while counter in others:
                    counter += 1

                all_workspaces.remove(name)
                all_workspaces.add(counter)
                output_wsset.remove(name)
                output_wsset.add(counter)
                yield str(name), str(counter)

            counter += 1


def rename_workspace(old: str, new: str):
    with open(os.devnull) as devnull:
        p = subprocess.Popen(["swaymsg", "rename", "workspace", old, "to", new], stdout=devnull, stderr=devnull)
        #p.wait()


def main():
    workspaces = get_workspaces()

    for rename_op in iter_renames_to_do(workspaces):
        rename_workspace(*rename_op)


if __name__ == '__main__':
    main()
