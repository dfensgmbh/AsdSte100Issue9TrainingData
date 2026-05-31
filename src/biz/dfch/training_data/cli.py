# Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# pylint: disable=C0413
# flake8: noqa: E402

"""Typer CLI application.

This module exposes the top-level :class:`typer.Typer` application as
``app``. The application is registered as the ``create`` console script
in ``pyproject.toml`` and can also be invoked via ``python -m
biz.dfch.training_data``.

The CLI can be launched from any working directory:

* The :class:`.env` file is located by walking upward from this module
  and (if not found) from the current working directory; an explicit
  path can be supplied with the global ``--env-file`` option.
* All file/directory arguments are resolved relative to the user's
  current working directory, which is the standard convention for a
  shell tool.
"""

from pathlib import Path
from typing import Annotated, Optional

from dotenv import find_dotenv, load_dotenv
import typer

from .commands import ambiguity
from .commands import compliance
from .commands import lexicon
from .commands import paragraph
from .commands import pos
from .commands import restriction
from .commands import rewrite
from .commands import choice
from .commands import query
from .commands import grammar
from .commands import verb
from .commands import category

from .info import Info


def _load_default_dotenv() -> None:
    """Load ``.env`` from the project (walking up from this file) or,
    failing that, from the current working directory.

    Existing environment variables are not overridden.
    """
    # ``find_dotenv(usecwd=False)`` walks up from the calling file's
    # directory; ``usecwd=True`` walks up from the user's CWD. We try
    # the file-anchored lookup first so the project's ``.env`` is found
    # when the user runs the CLI from any directory; CWD acts as a
    # fallback for the case where this module lives in an installed
    # location that does not contain a ``.env``.
    dotenv_path = find_dotenv(usecwd=False) or find_dotenv(usecwd=True)
    if dotenv_path:
        load_dotenv(dotenv_path)


# Load defaults at import time so module-level Typer options that read
# environment variables (via ``envvar=``) see the values.
_load_default_dotenv()


app = typer.Typer(
    name=Info.name,
    help=Info.description,
    epilog=Info.epilog,
    no_args_is_help=True,
)


@app.callback()
def _callback(
    ctx: typer.Context,
    env_file: Annotated[
        Optional[Path],
        typer.Option(
            "--env-file",
            help=(
                "Path to a .env file to load. When omitted, the .env "
                "closest to this module (and then to the current "
                "working directory) is used."
            ),
        ),
    ] = None,
) -> None:
    # We use ``callback`` to register the global ``--env-file`` option
    # and to make sure that Typer continues to show sub-commands when
    # there is only one sub-command registered.
    _ = ctx

    if env_file is not None:
        assert env_file.exists(), f"--env-file must exist: '{env_file}'."
        assert env_file.is_file(), f"--env-file is not a file: '{env_file}'."
        # ``override=True`` lets a user-supplied .env override values
        # that may have been loaded at import time.
        load_dotenv(env_file, override=True)


app.command(epilog=Info.epilog)(ambiguity)
app.command(epilog=Info.epilog)(lexicon)
app.command(epilog=Info.epilog)(pos)
app.command(epilog=Info.epilog)(rewrite)
app.command(epilog=Info.epilog)(compliance)
app.command(epilog=Info.epilog)(choice)
app.command(epilog=Info.epilog)(restriction)
app.command(epilog=Info.epilog)(paragraph)
app.command(epilog=Info.epilog)(query)
app.command(epilog=Info.epilog)(grammar)
app.command(epilog=Info.epilog)(verb)
app.command(epilog=Info.epilog)(category)


if __name__ == "__main__":
    app()
