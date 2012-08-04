#################################################################
# This file is part of plyr
# + a commnandline tool and library to download various sort of musicrelated metadata.
# + Copyright (C) [2011-2012]  [Christopher Pahl]
# + Hosted at: https://github.com/sahib/python-glyr
#
# plyr is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# plyr is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with plyr. If not, see <http://www.gnu.org/licenses/>.
#################################################################
cimport glyr as C

VERSION = (C.VERSION_MAJOR, C.VERSION_MINOR, C.VERSION_MIRCO)

def version():
    """
    libglyr\'s version string (with version number and release name)

    :returns: Something similar to
              ``Version 0.9.9 (Catholic Cat) of [Jun 24 2012] compiled at [22:55:56]``
    """
    return _stringify(<char*>C.glyr_version()) + ' {Cython Wrapped}'


def download(url):
    """
    Download a certain URL and return it as Cache.

    :url: The URL to download.
    :returns: A Cache instance, or None
    """
    byte_url = _bytify(url)
    cdef C.GlyrMemCache * c_cache = C.glyr_download(byte_url, NULL)
    if c_cache is not NULL:
        return cache_from_pointer(c_cache)
    else:
        return None


def type_is_image(type_str):
    """
    Check if a certain type descriptor is an image.

    :type_str: a type identifier.
    :returns: True or False
    """
    byte_type = _bytify(type_str)
    type_id = C.glyr_string_to_get_type(byte_type)
    return C.glyr_type_is_image(type_id)


# misc.h
def levenshtein_cmp(string, other):
    """
    Compute the levenshtein distance between two strings.

    See also: http://sahib.github.com/glyr/doc/html/libglyr-Misc.html

    :string: some string
    :other: another string
    :returns: An integer between 0 and max(len(string), len(other))
    """
    byte_string = _bytify(string)
    byte_other  = _bytify(other)
    return C.glyr_levenshtein_strcmp(byte_string, byte_other)


def levenshtein_normcmp(string, other):
    """
    Compute the levenshtein distance between two strings
    using additional normalization.

    See also: http://sahib.github.com/glyr/doc/html/libglyr-Misc.html

    :string: some string
    :other: another string
    :returns: An integer between 0 and [no-explicit-limit]
    """
    byte_string = _bytify(string)
    byte_other  = _bytify(other)
    return C.glyr_levenshtein_strnormcmp(byte_string, byte_other)


# testing.h - not even tested once
def call_url_generator(provider_name, get_type, Query query):
    'Do not use this, this is for testing purpose only'
    provider_name_bytes = _bytify(provider_name)
    get_type_id = C.glyr_string_to_get_type(get_type)
    return C.glyr_testing_call_url(provider_name_bytes, get_type_id, query._ptr())


def call_data_parser(provider_name, get_type, Query query, Cache cache):
    'Do not use this, this is for testing purpose only'
    provider_name_bytes = _bytify(provider_name)
    get_type_id = C.glyr_string_to_get_type(get_type)
    cdef C.GlyrMemCache * rc = NULL
    rc = C.glyr_testing_call_parser(provider_name_bytes, get_type_id, query._ptr(), cache._ptr())
    return cache_from_pointer(rc)
