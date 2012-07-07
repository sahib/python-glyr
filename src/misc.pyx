cimport glyr as C


VERSION = (C.VERSION_MAJOR, C.VERSION_MINOR, C.VERSION_MIRCO)

def version():
    return _stringify(<char*>C.glyr_version()) + ' {Cython Wrapped}'


def download(url):
    byte_url = _bytify(url)
    cdef C.GlyrMemCache * c_cache = C.glyr_download(byte_url, NULL)
    return cache_from_pointer(c_cache)


def type_is_image(type_str):
    byte_type = _bytify(type_str)
    type_id = C.glyr_string_to_get_type(byte_type)
    return C.glyr_type_is_image(type_id)


# misc.h
def levenshtein_cmp(string, other):
    byte_string = _bytify(string)
    byte_other  = _bytify(other)
    return C.glyr_levenshtein_strcmp(byte_string, byte_other)


def levenshtein_normcmp(string, other):
    byte_string = _bytify(string)
    byte_other  = _bytify(other)
    return C.glyr_levenshtein_strnormcmp(byte_string, byte_other)


# testing.h - not even tested once
def call_url_generator(provider_name, get_type, Query query):
    provider_name_bytes = _bytify(provider_name)
    get_type_id = C.glyr_string_to_get_type(get_type)
    return C.glyr_testing_call_url(provider_name_bytes, get_type_id, query._ptr())


def call_data_parser(provider_name, get_type, Query query, Cache cache):
    provider_name_bytes = _bytify(provider_name)
    get_type_id = C.glyr_string_to_get_type(get_type)
    cdef C.GlyrMemCache * rc = NULL
    rc = C.glyr_testing_call_parser(provider_name_bytes, get_type_id, query._ptr(), cache._ptr())
    return cache_from_pointer(rc)
