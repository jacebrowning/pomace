from typing import Tuple

from . import enums, shared


def mode_and_value() -> Tuple[str, str]:
    if not shared.cli:
        return "", ""

    choices = ["<cancel>"] + [mode.value for mode in enums.Mode]
    command = shared.cli.Bullet(
        prompt="\nSelect element locator: ",
        bullet=" ● ",
        choices=choices,
    )
    mode = command.launch()
    if mode == "<cancel>":
        print()
        return "", ""

    command = shared.cli.Input("\nValue to match: ")
    value = command.launch()
    print()
    return mode, value
