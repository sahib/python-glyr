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
cimport glyr as C

"""
Here are no functions, classes, docstrings,
Just the Provider dictionary, looking like that:

   'albumlist': {
               'optional' : ('album', 'title'),
               'required' : ('artist'),
               'provider' : [{
                      'key'     : 'm',
                      'name'    : 'musicbrainz',
                      'quality' : 95,
                      'speed'   : 95
               },
               {
                      ... next provider..
               }]
   },
   'lyrics': {
        ... next fetcher ...
   }

Note: This dictionary gets auto-generated on import
"""

PROVIDERS = {}

# Build a dictionary structure of providers
cdef C.GlyrFetcherInfo * _head = C.glyr_info_get()
cdef C.GlyrFetcherInfo * _node = _head
cdef C.GlyrSourceInfo * _source = NULL

# This looks kinda stupid in a language like Python.
cdef make_requirement_tuple(C.GLYR_FIELD_REQUIREMENT reqs):
    rc = []
    if reqs & C.REQUIRES_ARTIST:
        rc.append('artist')
    if reqs & C.REQUIRES_ALBUM:
        rc.append('album')
    if reqs & C.REQUIRES_TITLE:
        rc.append('title')
    return tuple(rc)

# And it even gets sillier
cdef make_optional_tuple(C.GLYR_FIELD_REQUIREMENT reqs):
    rc = []
    if reqs & C.OPTIONAL_ARTIST:
        rc.append('artist')
    if reqs & C.OPTIONAL_ALBUM:
        rc.append('album')
    if reqs & C.OPTIONAL_TITLE:
        rc.append('title')
    return tuple(rc)

while _node is not NULL:
    _str_name = _stringify(_node.name)
    _source = _node.head
    PROVIDERS[_str_name] = {}
    PROVIDERS[_str_name]['optional'] = make_optional_tuple(_node.reqs)
    PROVIDERS[_str_name]['required'] = make_requirement_tuple(_node.reqs)
    PROVIDERS[_str_name]['providers'] = []
    while _source is not NULL:
        PROVIDERS[_str_name]['providers'].append({
                'name'   : _stringify(_source.name),
                'key'    : chr(_source.key),
                'quality': _source.quality,
                'speed'  : _source.speed,
        })
        _source = _source.next
    _node = _node.next

if _head is not NULL:
    C.glyr_info_free(_head)
