cimport glyr as C

from libc.string cimport memcpy


cdef cache_from_pointer(C.GlyrMemCache * ptr):
    py_cache = Cache()
    py_cache._cm = ptr
    return py_cache


# Conversion utilty, being used only in the Wrapper
cdef cache_list_from_pointer(C.GlyrMemCache * head):
    """
    Convert a linked list (next/prev) from C
    to a usable Python-List
    """
    result_list = []

    cdef C.GlyrMemCache * item = head
    while item is not NULL:
        result_list.append(cache_from_pointer(item))
        item = item.next

    return result_list


cdef class Cache:

    ###########################################################################
    #                             Initialization                              #
    ###########################################################################

    cdef C.GlyrMemCache * _cm

    def __cinit__(self, **kwargs):
        self._cm = C.glyr_cache_new()

        for key, value in kwargs.items():
            Cache.__dict__[key].__set__(self, value)

    def __dealloc__(self):
        C.glyr_cache_free(self._cm)

    ###########################################################################
    #                        Other methods / functions                        #
    ###########################################################################

    # TODO: __repr__

    def update_checksum(self):
        C.glyr_cache_update_md5sum(self._cm)

    def print_cache(self):
        C.glyr_cache_print(self._cm)

    def write(self, path):
        byte_path = _bytify(path)
        C.glyr_cache_write(self._cm, byte_path)

    ###########################################################################
    #                               Properties                                #
    ###########################################################################

    property duration:
        def __set__(self,  duration):
            self._cm.duration = duration
        def __get__(self):
            return self._cm.duration

    property rating:
        def __set__(self,  rating):
            C.glyr_cache_set_rating(self._cm, rating)
        def __get__(self):
            return self._cm.rating

    property is_image:
        # You really should not set this
        def __get__(self):
            return self._cm.is_image

    property image_format:
        def __set__(self,  image_format):
            byte_image_format = _bytify(image_format)
            C.glyr_cache_set_img_format(self._cm, byte_image_format)
        def __get__(self):
            return _stringify(self._cm.img_format)

    property checksum:
        # You usually should use update_checksum(),
        # this is only if you already luckily have some
        # correct checksum lying there by accident.
        def __set__(self,  checksum):
            cdef char byte_checksum[33]
            C.glyr_string_to_md5sum(byte_checksum, checksum)
            memcpy(self._cm.md5sum, byte_checksum, 16)
        def __get__(self):
            return _stringify(C.glyr_md5sum_to_string(self._cm.md5sum))

    property data_type:
        def __set__(self,  type_str):
            byte_type_str = _bytify(type_str)
            cdef C.GLYR_DATA_TYPE type_id = C.glyr_string_to_data_type(byte_type_str)
            C.glyr_cache_set_type(self._cm, type_id)
        def __get__(self):
            return _stringify(C.glyr_data_type_to_string(self._cm.data_type))

    property data:
        def __set__(self, data):
            C.glyr_cache_set_data(self._cm, data, len(data))
        def __get__(self):
            return self._cm.data

    property size:
        def __set__(self,  size):
            self._cm.size = size
        def __get__(self):
            return self._cm.size

    property source_url:
        def __set__(self,  dsrc):
            byte_dsrc = _bytify(dsrc)
            C.glyr_cache_set_dsrc(self._cm, byte_dsrc)
        def __get__(self):
            return self._cm.dsrc

    property provider:
        def __set__(self,  prov):
            byte_prov = _stringify(prov)
            C.glyr_cache_set_prov(self._cm, byte_prov)
        def __get__(self):
            return _stringify(self._cm.prov)

    property is_cached:
        def __set__(self,  is_cached):
            self._cm.cached = is_cached
        def __get__(self):
            return self._cm.cached

    property timestamp:
        def __set__(self,  timestamp):
            self._cm.timestamp = timestamp
        def __get__(self):
            return self._cm.timestamp
