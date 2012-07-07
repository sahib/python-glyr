cimport glyr as C

cdef int _db_proxy_callback(C.GlyrQuery * query, C.GlyrMemCache * cache, void * user_pointer):
    cdef object py_func = <object>user_pointer
    pyc = cache_from_pointer(cache)
    pyq = query_from_pointer(query)
    return py_func(pyq, pyc)


cdef class Database:
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
        return cache_from_pointer(C.glyr_db_make_dummy())

    def lookup(self, Query query):
        cdef C.GlyrMemCache * rc = NULL
        rc = C.glyr_db_lookup(self._ptr(), query._ptr())
        return cache_list_from_pointer(rc)

    def insert(self, Query query, Cache cache):
        C.glyr_db_insert(self._ptr(), query._ptr(), cache._ptr())

    def delete(self, Query query):
        return C.glyr_db_delete(self._ptr(), query._cqp)

    def edit(self, Query query, Cache cache):
        return C.glyr_db_edit(self._ptr(), query._cqp, cache._ptr())

    def foreach(self, py_func):
        C.glyr_db_foreach(self._ptr(), _db_proxy_callback, <void*>py_func)

    def replace(self, md5sum, Query query, Cache cache):
        if len(md5sum) < 33:
            raise ValueError('checksum has to be at least 33 bytes long')

        cdef unsigned char byte_cksum[16]
        py_string_ckssum = _bytify(md5sum)
        C.glyr_string_to_md5sum(py_string_ckssum, byte_cksum)
        C.glyr_db_replace(self._ptr(), byte_cksum, query._cqp, cache._ptr())
