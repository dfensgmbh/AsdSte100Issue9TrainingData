# Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.


from dataclasses import dataclass


@dataclass
class Info:
    """Program information."""

    name = "ASD-STE100 Issue 9 Training Data"
    version = "0.1.0"
    description = (
        f"{name}, v{version}. An ASD-STE100 Issue 9 Training Data creator."
    )
    epilog = (
        "Copyright 2026 Ronald Rink, d-fens GmbH, "
        "https://github.com/dfensgmbh/AsdSte100Issue9TrainingData"
        ". "
        "Licensed under AGPLv3."
    )
