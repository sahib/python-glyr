#################################################################
# This file is part of plyr
# + a commnandline tool and library to download various sort of musicrelated metadata.
# + Copyright (C) [2011-2016]  [Christopher Pahl]
# + Hosted at: https://github.com/sahib/python-glyr
#
# plyr is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# plyr is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with plyr. If not, see <http://www.gnu.org/licenses/>.
#################################################################
from glyr cimport glyr_init
from glyr cimport glyr_cleanup
from libc.stdlib cimport atexit

# Initialize Library
glyr_init()

# Register destroyage using the C-level atexit
atexit(<void (*)() nogil>glyr_cleanup)

# Imports already Cache
include "wrapper.pyx"
include "query.pyx"
include "misc.pyx"
include "database.pyx"
include "provider.pyx"

# This module is (surprise!) empty, and just there
# to have only one Extension in setup.py
# This is the only file therefore that you gonna include
