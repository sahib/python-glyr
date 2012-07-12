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
    """
    A Cache is one result or item retrieved by libglyr

    It encapsulates various properties like ,,data'', ,,checksum''
    or ,,image_format'' and quite some more.

    It can be instanciated directly, but there is no valid use to do so currently.
    """

    ###########################################################################
    #                             Initialization                              #
    ###########################################################################

    cdef C.GlyrMemCache * _cm

    def __cinit__(self, **kwargs):
        self._cm = C.glyr_cache_new()

        for key, value in kwargs.items():
            Cache.__dict__[key].__set__(self, value)

    cdef C.GlyrMemCache * _ptr(self):
        return self._cm

    def __dealloc__(self):
        C.glyr_cache_free(self._ptr())

    ###########################################################################
    #                        Other methods / functions                        #
    ###########################################################################

    def update_checksum(self):
        """
        Update the checksum manually.

        This should never be necessary in this wrapper though.
        """
        C.glyr_cache_update_md5sum(self._ptr())

    def print_cache(self):
        """
        Pretty print of the cache to stdout.

        There is no __repr__ at the moment.
        """
        C.glyr_cache_print(self._ptr())

    def write(self, path):
        """
        Write item content (data) to a valid path.

        :path: Must be a valid path.
        """
        byte_path = _bytify(path)
        C.glyr_cache_write(self._ptr(), byte_path)

    ###########################################################################
    #                               Properties                                #
    ###########################################################################

    property duration:
        'Duration in seconds, only filled for "tracklist", otherwise 0.'
        def __set__(self,  duration):
            self._ptr().duration = duration
        def __get__(self):
            return self._ptr().duration

    property rating:
        """
        The rating of this item, this is for you to set, libglyr
        will always set it to 0 by default. The only case where
        rating has a semantic meaning is for Database lookups:

        If more than one item is requested, the items are returned
        sorted by the rating (highest rating first), and as second
        criteria by the timestamp, so the item with the highest rating,
        and the newest timestamp is always first.

        This is useful to insert "dummies" to the db, in case some item
        was not found.
        """
        def __set__(self,  rating):
            C.glyr_cache_set_rating(self._ptr(), rating)
        def __get__(self):
            return self._ptr().rating

    property is_image:
        'A boolean. Set to true if this item contains image data.'
        # You really should not set this
        def __get__(self):
            return self._ptr().is_image

    property image_format:
        """
        The format of the image, might be one of: ::

            [png, jpeg, gif, tiff]

        """
        def __set__(self,  image_format):
            byte_image_format = _bytify(image_format)
            C.glyr_cache_set_img_format(self._ptr(), byte_image_format)
        def __get__(self):
            return _stringify(self._ptr().img_format)

    property checksum:
        """
        A 16 byte md5sum checksum in hexadecimal string-representation of the data field.

        You usually should use update_checksum(),
        this is only if you already luckily have some
        correct checksum lying there by accident.
        """
        def __set__(self,  checksum):
            cdef char byte_checksum[33]
            C.glyr_string_to_md5sum(byte_checksum, checksum)
            memcpy(self._ptr().md5sum, byte_checksum, 16)
        def __get__(self):
            return _stringify(C.glyr_md5sum_to_string(self._ptr().md5sum))

    property data_type:
        'The type of data - this may differ from the get_type'
        def __set__(self,  type_str):
            byte_type_str = _bytify(type_str)
            cdef C.GLYR_DATA_TYPE type_id = C.glyr_string_to_data_type(byte_type_str)
            C.glyr_cache_set_type(self._ptr(), type_id)
        def __get__(self):
            return _stringify(<char*>C.glyr_data_type_to_string(self._ptr().data_type))

    property data:
        'Actual data as bytestring. Also settable.'
        def __set__(self, data):
            C.glyr_cache_set_data(self._ptr(), data, len(data))
        def __get__(self):
            if self._ptr().data is not NULL:
                return self._ptr().data[:self._ptr().size]
            else:
                return b''

    property size:
        """
        Size in bytes of data - this is not useful in Python, as you could do also: ::

            len(mycache.data)

        This attribute is not settable, since you could screw things up.
        """
        def __get__(self):
            return self._ptr().size

    property source_url:
        'The URL where this items was retrieved from.'
        def __set__(self,  dsrc):
            byte_dsrc = _bytify(dsrc)
            C.glyr_cache_set_dsrc(self._ptr(), byte_dsrc)
        def __get__(self):
            return _stringify(self._ptr().dsrc)

    property provider:
        'The name of the provider where this items was retrieved from.'
        def __set__(self,  prov):
            byte_prov = _stringify(prov)
            C.glyr_cache_set_prov(self._ptr(), byte_prov)
        def __get__(self):
            return _stringify(self._ptr().prov)

    property is_cached:
        'Did this item come from a local database?'
        def __set__(self,  is_cached):
            self._ptr().cached = is_cached
        def __get__(self):
            return self._ptr().cached

    property timestamp:
        'If is_cached is True, a timestamp of the insertion sec.ms, otherwise 0.'
        def __set__(self,  timestamp):
            self._ptr().timestamp = timestamp
        def __get__(self):
            return self._ptr().timestamp
