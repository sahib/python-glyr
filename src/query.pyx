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

from cpython cimport bool

include "cache.pyx"

# This is a proxy callback that reads a PyObject from
# a user_pointer and calls it
# This function is called from C code
cdef int _actual_callback(C.GlyrMemCache * c, C.GlyrQuery * q) with gil:
    'Proxy callback, calling set callable object, and returning rc to C-Side'

    py_callback = <object>q.callback.user_pointer
    pyq = query_from_pointer(q)
    pyc = cache_from_pointer(c, False)

    status = py_callback(pyc, pyq)

    if status == 'post_stop':
        return C.E_STOP_POST
    elif status == 'pre_stop':
        return C.E_STOP_PRE
    else:
        return C.E_OK


cdef query_from_pointer(C.GlyrQuery * query):
    'Internally used, wraps a GlyrQuery into a Query'
    pyq = Query(new_query=False)
    pyq._cqp = query
    return pyq


cdef C.GLYR_NORMALIZATION _convert_py_to_normenum(object python_tuple):
    'Convert a tuple of ("aggressive", "artist", "album") to a enum'
    #cdef C.GLYR_NORMALIZATION en = <C.GLYR_NORMALIZATION>0
    cdef unsigned en = 0
    for elem in python_tuple:
        if elem == 'aggressive':
            en |= C.NORMALIZE_AGGRESSIVE
        elif elem == 'moderate':
            en |= C.NORMALIZE_MODERATE
        elif elem == 'none':
            en |= C.NORMALIZE_NONE
        elif elem == 'artist':
            en |= C.NORMALIZE_ARTIST
        elif elem == 'album':
            en |= C.NORMALIZE_ALBUM
        elif elem == 'title':
            en |= C.NORMALIZE_TITLE
        elif elem == 'all':
            en |= C.NORMALIZE_ALL

    return <C.GLYR_NORMALIZATION>en


cdef object _convert_normenum_to_py(C.GLYR_NORMALIZATION norm):
    py_tup = []
    if norm & C.NORMALIZE_AGGRESSIVE:
        py_tup.append('aggressive')
    if norm & C.NORMALIZE_MODERATE:
        py_tup.append('moderate')
    if norm & C.NORMALIZE_NONE:
        py_tup.append('none')
    if norm & C.NORMALIZE_ARTIST:
        py_tup.append('artist')
    if norm & C.NORMALIZE_ALBUM:
        py_tup.append('album')
    if norm & C.NORMALIZE_TITLE:
        py_tup.append('title')
    if norm & C.NORMALIZE_ALL:
        py_tup.append('all')

    return tuple(py_tup)

cdef class Query:
    """
    A Query is an object defining a search term for libglyr.
    As a minimum the ,,get_type'' and ,,artist'' and/or the
    ,,album'' or ,,title'' properties shall be set.

    The constructor takes a list of keywords, these keywords
    are the same as the propertynames below.

    A Query can be committed with commit(), which blocks till
    execution is done. On the way a callback method may be
    called as set by the equally named property. One may cancel
    a Query from another thread by calling cancel() on it,
    or returning a value other than 0 from the callback.
    """
    # Actual underlying Query
    cdef C.GlyrQuery _cq
    cdef C.GlyrQuery * _cqp
    cdef Database _db_prop
    cdef bool _new_query

    # Allocation on C-Side
    def __cinit__(self, new_query=True, **kwargs):
        if new_query:
            C.glyr_query_init(&self._cq)
            self._cqp = &self._cq
            self._db_prop = None
            self._new_query = new_query

            for key, value in kwargs.items():
                Query.__dict__[key].__set__(self, value)

    cdef C.GlyrQuery * _ptr(self):
        return self._cqp

    # Deallocation on C-Side
    def __dealloc__(self):
        if self._new_query:
            C.glyr_query_destroy(self._cqp)
            self._cqp = NULL

    def __repr__(self):
        # I find this fascinating.
        return '<' +  '\n'.join([str((key, Query.__dict__[key].__get__(self)))
            for key, value in Query.__dict__.items()
            if 'getset_descriptor' in str(type(value))]) + '>'

    ###########################################################################
    #         Lots of properties, these wrap the glyr_opt_* family()          #
    ###########################################################################

    property get_type:
        """
        The type of metadata you want to retrieve.

        For a complete list use: ::

          print(list(plyr.PROVIDER.keys()))

        :get_type_value: Any of the above strings, may do nothing with a bad type!
        """
        def __set__(self, value):
            if hasattr(value, 'upper'):
                byte_value = _bytify(value)
                actual_type = C.glyr_string_to_get_type(byte_value)
            else:
                actual_type = value

            C.glyr_opt_type(self._ptr(), actual_type)
        def __get__(self):
            return _stringify(<char*>C.glyr_get_type_to_string(self._ptr().type))

    property number:
        """
        The number of items you want to retrieve, 0 for infinite, by default 1

        :number: Any number, < 0 will be clamped to 0.
        """
        def __set__(self, int number):
            C.glyr_opt_number(self._ptr(), number)
        def __get__(self):
            return self._ptr().number

    property max_per_plugins:
        """
        How many items a single provider may retrieve (not very useful normally)

        :max_per_plugins: Any number, < 0 will be clamped to a high number.
        """
        def __set__(self, int max_per_plugins):
            C.glyr_opt_plugmax(self._ptr(), max_per_plugins)
        def __get__(self):
            return self._ptr().plugmax

    property verbosity:
        """
        How verbose the library will print status messages.

        0 -> no messages except fatal errors
        1 -> warnings only
        2 -> basic info
        3 -> more info
        4 -> very detailed debug messages

        :verbosity: an integer in [0..4]
        """
        def __set__(self, int verbosity):
            C.glyr_opt_verbosity(self._ptr(), verbosity)
        def __get__(self):
            return self._ptr().verbosity

    property fuzzyness:
        """
        Max levenshtein distance difference for fuzzy matching.

        libglyr features fuzzy matching to enhance search results.
        Look at the string "Equilibrium" and the accidentally mistyped version "Aquillibriu":
        Those strings will be compares using the "Levenshtein distance"
        (http://en.wikipedia.org/wiki/Levenshtein_distance) which basically counts the number of insert,
        substitute and delete operations to transform Equilibrium"" into "Aquillibriu".
        The distance in this case is 3 since three edit-operations are needed
        (one insert, substitute and deletion)
        The fuzziness parameter is the maximum distance two strings may have to match.
        A high distance (like about 10) matches even badly mistyped strings, but also introduces bad results. Low settings
        however will omit some good results.
        The default values is currently 4. To be more secure some correction is applied:

        Example:

        - artist: Adele - album: 19
        - artist: Adele - album: 21
        - lv-distance = 2 which is <= 4
        - But since the lv-distance is the same as the length "21" it won't match.

        :fuzzyness: a positive integer
        """
        def __set__(self, int fuzzyness):
            C.glyr_opt_fuzzyness(self._ptr(), fuzzyness)
        def __get__(self):
            return self._ptr().fuzzyness

    property img_size:
        """
        Limits min. and max. size of images in pixel.

        Please note: This is used by glyr only as a hint. There
        is no guarantee that the actual image is between this limits.

        :size_tuple: A tuple of a min. and max. in pixel (e.g. (100, 500))
        """
        def __set__(self, size_tuple):
            C.glyr_opt_img_minsize(self._ptr(), size_tuple[0])
            C.glyr_opt_img_maxsize(self._ptr(), size_tuple[1])
        def __get__(self):
            return [self._ptr().img_max_size, self._ptr().img_min_size]

    property parallel:
        """
        Max parallel downloads handles that glyr may open

        :parallel: A positive integer, do not try 0
        """
        def __set__(self, int parallel):
            C.glyr_opt_parallel(self._ptr(), parallel)
        def __get__(self):
            return self._ptr().parallel

    property timeout:
        """
        Max timeout in seconds to wait before a download handle is canceled.

        :timeout: A timeout in seconds
        """
        def __set__(self, int timeout):
            C.glyr_opt_timeout(self._ptr(), timeout)
        def __get__(self):
            return self._ptr().timeout

    property redirects:
        """
        Max redirects to allow for download handles.

        :redirects: A positive integer, do not try 0
        """
        def __set__(self, int redirects):
            C.glyr_opt_redirects(self._ptr(), redirects)
        def __get__(self):
            return self._ptr().redirects

    property force_utf8:
        """
        For textitems only: try to convert input to utf-8 always, throw away if invalidly encoded.

        :force_utf8: True or False
        """
        def __set__(self, bool force_utf8):
            C.glyr_opt_force_utf8(self._ptr(), force_utf8)
        def __get__(self):
            return self._ptr().force_utf8

    property qsratio:
        """
        A float between 0.0 and 1.0 that influences in which way providers are triggered.

        0.0 means best speed, i.e. querying google for covers at first, 1.0 will query the little bit
        slower last.fm, which will deliver almost always HQ items.

        :qsratio: Any number between 0.0 and 1.0, do not except magic improvements.
        """
        def __set__(self, float qsratio):
            C.glyr_opt_qsratio(self._ptr(), qsratio)
        def __get__(self):
            return self._ptr().qsratio

    property db_autoread:
        """
        A boolean, if set to True a local cache is queried first.

        If the database property is not set, this option has no effect at all.
        Defaults to True.

        :db_autoread: True or False
        """
        def __set__(self, bool db_autoread):
            C.glyr_opt_db_autoread(self._ptr(), db_autoread)
        def __get__(self):
            return self._ptr().db_autoread

    property db_autowrite:
        """
        Auto-write downloaded items to database. Defaults to True.

        If the database property is not set, this option has no effect at all.

        :db_autowrite: True or False
        """
        def __set__(self, bool db_autowrite):
            C.glyr_opt_db_autowrite(self._ptr(), db_autowrite)
        def __get__(self):
            return self._ptr().db_autowrite

    property database:
        """
        Set a local database to be used by this query.

        :database: An instance of plyr.Database
        """
        def __set__(self, Database database):
            if database is not None:
                self._db_prop = database
                C.glyr_opt_lookup_db(self._ptr(), database._ptr())

        def __get__(self):
            return self._db_prop

    property language_aware_only:
        """
        Only query providers that have localized content

        :language_aware_only: True or False
        """
        def __set__(self, bool lang_aware_only):
            C.glyr_opt_lang_aware_only(self._ptr(), lang_aware_only)
        def __get__(self):
            return self._ptr().lang_aware_only

    property language:
        """
        The language you want the items in, as ISO 639-1 language code (e.g. 'de', 'en'...)

        Note: There are only a few localized providers,
        and stuff like lyrics is localized anyway,
        but for example artist biographies are available in different languages.

        When lang_aware_only is not set, all other providers are used too.

        :language: Any of "en;de;fr;es;it;jp;pl;pt;ru;sv;tr;zh"
        """
        def __set__(self, language):
            byte_language = _bytify(language)
            C.glyr_opt_lang(self._ptr(), byte_language)
        def __get__(self):
            return _stringify(self._ptr().lang)

    property proxy:
        """
        If you need to a proxy set, use it here.

        :proxy_string: Passed in the form: [protocol://][user:pass@]yourproxy.domain[:port]
        """
        def __set__(self, proxy):
            byte_proxy = _bytify(proxy)
            C.glyr_opt_proxy(self._ptr(), byte_proxy)
        def __get__(self):
            return _stringify(self._ptr().proxy)

    property artist:
        """
        Set the artist to search for.

        :artist: Any valid string.
        """
        def __set__(self, value):
            byte_value = _bytify(value)
            C.glyr_opt_artist(self._ptr(), byte_value)
        def __get__(self):
            return _stringify(self._ptr().artist)

    property album:
        """
        Set the album to search for.

        :album: Any valid string.
        """
        def __set__(self, value):
            byte_value = _bytify(value)
            C.glyr_opt_album(self._ptr(), byte_value)
        def __get__(self):
            return _stringify(self._ptr().album)

    property title:
        """
        Set the title to search for.

        :title: Any valid string.
        """
        def __set__(self, value):
            byte_value = _bytify(value)
            C.glyr_opt_title(self._ptr(), byte_value)
        def __get__(self):
            return _stringify(self._ptr().title)

    property providers:
        """
        Pass a list of provider names to forbid glyr to search other providers.

        'all' can be used to enable all providers,
        other providers can be prepended with a '-' to exclude them from the list,

        To find out providernames programmatically use the PROVIDERS dict.

        Examples: ::

            ['lastfm', 'google']
            ['all', '-lastfm']


        See also: http://sahib.github.com/glyr/doc/html/libglyr-Glyr.html#glyr-opt-from
        """
        def __set__(self, value_list):
            provider_string = _bytify(';'.join(value_list))
            C.glyr_opt_from(self._ptr(), provider_string)
        def __get__(self):
            return _stringify(self._ptr().providers).split(';')

    property callback:
        """
        Set a function that is called when an item is readily downloaded.

        The function must take two arguments: ::

            def funny_smelling_callback(cache, query):
                # query is the Query you used to search this.
                # cache is the actual item.

                # One may return:
                #  - 'ok'        -> continue search
                #  - 'post_stop' -> append item to results, and stop
                #  - 'pre_stop'  -> stop immediately, return all results before
                #
                # Returning nothing is the same as 'ok'
                return 'ok'

        :py_func: a method, function or any object that implements __call__()
        """
        # Save callable object as user_pointer
        # just cast it back if you do __get__
        def __set__(self, object py_func):
            C.glyr_opt_dlcallback(self._ptr(), <C.DL_callback>_actual_callback, <void*>py_func)
        def __get__(self):
            if self._ptr().callback.user_pointer is NULL:
                return None
            else:
                return <object>self._ptr().callback.user_pointer


    property allowed_formats:
        """
        For image-fetchers only: limit image formats to a list of formats.

        Default: ::

          ['png', 'jpg', 'gif', 'jpeg']

        :allowed_formats: a list of image format endings
        """
        def __set__(self,  allowed_formats):
            allowed_list = _bytify(';'.join(allowed_formats))
            C.glyr_opt_allowed_formats(self._ptr(), allowed_list)
        def __get__(self):
            return _stringify(self._ptr().allowed_formats).split(';')

    property useragent:
        """
        Set a certain user-agent on your own

        Note: Some providers like discogs need a proper useragent set.
        Use with care therefore.

        :useragent: A string like "libglyr/0.9.9 (Catholic Cat) +https://www.github.com/sahib/glyr"
        """
        def __set__(self,  useragent):
            byte_useragent = _bytify(useragent)
            C.glyr_opt_useragent(self._ptr(), byte_useragent)
        def __get__(self):
            return _stringify(self._ptr().useragent)

    property musictree_path:
        """
        Set the path to a audiofile, where a folder.jpg or similar may be near.

        libglyr supports searching through the filesystem beginning with a certain file,
        or a directory containing e.g. folder.jpeg and some audio files.

        See a more detailed description here:
        http://sahib.github.com/glyr/doc/html/libglyr-Glyr.html#glyr-opt-musictree-path

        :musictree_path: Something like ~/HD/Musik/DevilDriver/Beast/BlackSoulChoir.mp3
        """
        def __set__(self,  musictree_path):
            byte_musictree_path = _bytify(musictree_path)
            C.glyr_opt_musictree_path(self._ptr(), byte_musictree_path)
        def __get__(self):
            return _stringify(self._ptr().musictree_path)

    property normalize:
        """
        Define how much input artist/album/title is normalized.

        Normalization can be enabled for artist and album only with e.g.: ::

            ('artist', 'album', 'moderate')

        :norm: A tuple containg one, or many of "artist", "album",
               "title", "aggressive", "moderate", "none"
        """
        def __set__(self, norm):
            cdef C.GLYR_NORMALIZATION en = <C.GLYR_NORMALIZATION>0
            en = _convert_py_to_normenum(norm)
            C.glyr_opt_normalize(self._ptr(), en)
        def __get__(self):
            return _convert_normenum_to_py(self._ptr().normalization)

    property do_download:
        """
        Download images or just return links to them?
        """
        def __set__(self, bool do_download):
            C.glyr_opt_download(self._ptr() , do_download)
        def __get__(self):
            return self._ptr().download

    ###########################################################################
    #                              other methods                              #
    ###########################################################################

    def commit(self):
        """
        Commit a configured Query.
        This function blocks until execution is done.

        :returns: a list of byteblobs or [] on error,
                  use error to find out what happened.
        """
        self_ptr = self._ptr()

        with nogil:
            item_list = C.glyr_get(self_ptr, NULL, NULL)

        return cache_list_from_pointer(item_list)

    def cancel(self):
        """
        Stop an already started query from another thread.

        This does not make commit() return immediately, it's rather a
        soft shutdown that finishes already running parsers, but do
        not download any new data.
        """
        C.glyr_signal_exit(self._ptr())

    property error:
        'String representation of internally happened error (might be "No Error")'
        def __get__(self):
            rc = _stringify(<char*>C.glyr_strerror(self._ptr().q_errno))
            if rc == 'No error':
                return ''
            else:
                return rc
