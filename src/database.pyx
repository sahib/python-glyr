cimport glyr as C

cdef int _db_proxy_callback(C.GlyrQuery * query, C.GlyrMemCache * cache, void * user_pointer) with gil:
    'Internally used proxy callback of foreach callback'
    cdef object py_func = <object>user_pointer
    pyc = cache_from_pointer(cache)
    pyq = query_from_pointer(query)

    status = py_func(pyq, pyc)
    if status:
        return 0
    else:
        return -1


cdef class Database:
    """
    Database gives you access to a local cache of downloaded
    (or generated) items. Under the hood a SQLite Database is used.
    """
    cdef C.GlyrDatabase * _cdb

    NAME = 'metadata.db'

    def __cinit__(self, root_path):
        byte_root_path = _bytify(root_path)
        self._cdb = C.glyr_db_init(byte_root_path)

    cdef C.GlyrDatabase * _ptr(self):
        return self._cdb

    def __dealloc__(self):
        C.glyr_db_destroy(self._ptr())

    def make_dummy(self):
        """
        Generate a Dummy Cache with a rating of -1.

        This is useful to insert 'empty' items, indicating
        a query that led to no results. (So it does not get re-queried)

        :returns: An empty Cache
        """
        return cache_from_pointer(C.glyr_db_make_dummy())

    def lookup(self, Query query):
        """
        Lookup data from the cache.

        It uses following fields from Query:

        - artist / album / title / get_type: they must be filled accordingly
        - donwload: If true search for images, else search for links
        - number: The number of items to search for.
        - from: Limit providers.

        See also: http://sahib.github.com/glyr/doc/html/libglyr-Cache.html#glyr-db-lookup

        :query: the search query
        :returns: a list of caches
        """
        cdef C.GlyrMemCache * rc = NULL
        rc = C.glyr_db_lookup(self._ptr(), query._ptr())
        return cache_list_from_pointer(rc)

    def insert(self, Query query, Cache cache):
        """
        Insert a Cache manually into the database.

        :cache: The Cache to insert.
        :query: The Query describing artist, album, title, get_type
        """
        C.glyr_db_insert(self._ptr(), query._ptr(), cache._ptr())

    def delete(self, Query query):
        """
        Same as lookup, but deletes stuff instead.

        See also: http://sahib.github.com/glyr/doc/html/libglyr-Cache.html#glyr-db-delete

        :query: the search query)
        :returns: the number of deleted items
        """
        return C.glyr_db_delete(self._ptr(), query._ptr())

    def edit(self, Query query, Cache cache):
        """
        Replace a cache (or even a list of caches) with a new one.

        See also: http://sahib.github.com/glyr/doc/html/libglyr-Cache.html#glyr-db-edit

        :query: The search query.
        :cache: The new cache to replace the old one.
        :returns: The number of replaced caches.
        """

        self_ptr = self._ptr()
        query_ptr = query._ptr()
        cache_ptr = cache._ptr()
        cdef int rc = 0
        with nogil:
            rc = C.glyr_db_edit(self_ptr, query_ptr, cache_ptr)

        return rc

    def foreach(self, py_func):
        """
        Iterate over all items in the database, calling a callback on each item.

        The callback needs to take two arguments: ::

            def foreach_callback(query, cache):
                # query is the original query used to search this item
                # but only with reconstructable fields filled.
                # cache is the actual item including the data.
                pass

        :py_func: A callable object, like a function.
        """
        self_ptr = self._ptr()

        with nogil:
            C.glyr_db_foreach(self_ptr, _db_proxy_callback, <void*>py_func)

    def replace(self, md5sum, Query query, Cache cache):
        """
        Replace a cache from which you know the md5sum.

        See also: http://sahib.github.com/glyr/doc/html/libglyr-Cache.html#glyr-db-replace

        :md5sum: A 32 char long string, being a checksum in hexrepr.
        :query: The search query.
        :cache: The Cache to replace the item.
        """
        if len(md5sum) < 33:
            raise ValueError('checksum has to be at least 33 bytes long')

        cdef unsigned char byte_cksum[16]
        py_string_ckssum = _bytify(md5sum)
        C.glyr_string_to_md5sum(py_string_ckssum, byte_cksum)
        C.glyr_db_replace(self._ptr(), byte_cksum, query._ptr(), cache._ptr())
