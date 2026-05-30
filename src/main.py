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

"""Entry point."""

from dotenv import load_dotenv
import typer

from biz.dfch.training_data.commands import ambiguity
from biz.dfch.training_data.commands import compliance
from biz.dfch.training_data.commands import lexicon
from biz.dfch.training_data.commands import paragraph
from biz.dfch.training_data.commands import pos
from biz.dfch.training_data.commands import restriction
from biz.dfch.training_data.commands import rewrite
from biz.dfch.training_data.commands import choice
from biz.dfch.training_data.commands import query


from biz.dfch.training_data.info import Info

load_dotenv()

app = typer.Typer(
    name=Info.name,
    help=Info.description,
    epilog=Info.epilog,
    no_args_is_help=True,
)


@app.callback()
def _callback(ctx: typer.Context):
    # We use `callback` only to make sure that `typer` continues to show
    # "sub-commands" when there is only one "sub-command".

    _ = ctx

    return


app.command(epilog=Info.epilog)(ambiguity)
app.command(epilog=Info.epilog)(lexicon)
app.command(epilog=Info.epilog)(pos)
app.command(epilog=Info.epilog)(rewrite)
app.command(epilog=Info.epilog)(compliance)
app.command(epilog=Info.epilog)(choice)
app.command(epilog=Info.epilog)(restriction)
app.command(epilog=Info.epilog)(paragraph)
app.command(epilog=Info.epilog)(query)


if __name__ == "__main__":
    app()
