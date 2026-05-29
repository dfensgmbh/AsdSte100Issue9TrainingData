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

"""commands module."""

from .ambiguity import ambiguity
from .args import NameArg
from .args import OutputArg
from .args import OverwriteArg
from .compliance import compliance
from .lexicon import lexicon
from .paragraph import paragraph
from .pos import pos
from .restriction import restriction
from .rewrite import rewrite
from .choice import choice

__all__ = [
    "ambiguity",
    "compliance",
    "lexicon",
    "NameArg",
    "OutputArg",
    "OverwriteArg",
    "paragraph",
    "pos",
    "restriction",
    "rewrite",
    "choice",
]
