#!/usr/bin/env python
try:
    import glyr.cglyr as C
except ImportError as e:
    print('Unable to import glyr bindings:',e)
else:
    print(C.glyr_version())
