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
