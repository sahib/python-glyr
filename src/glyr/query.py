#!/usr/bin/env python
# encoding: utf-8
"""
Query Module
Send actual queries to libglyr
"""
import cglyr as C
import shared

from cache import Cache

def _lookup_type_from_string(type_str):
    """
    Convert a type string (e.g. 'cover')
    to a GLYR_GET_TYPE enum value

    Returns: GLYR_GET_UNSURE on failure
    """
    type_id = C.GLYR_GET_UNSURE
    info = C.glyr_info_get()
    node = info
    while node:
        if type_str == node.name:
            type_id = node.type
            break
        node = node.next

    C.glyr_info_free(info)
    return type_id
                    
def _opt_type_wrapper(query, type_str):
    """
    Converts type from str to an id 
    and pass it to the C-Routine
    """
    type_id = C.glyr_string_to_get_type(type_str)
    C.glyr_opt_type(query, type_id)

def _opt_dlcallback_wrapper(query, callback):
    """
    Wrap the required 2 argument function,
    to the actual opt_function
    """
    C.glyr_opt_pycallback(query, _dl_callback_proxy, callback)

OPT_DICT = {
        'dlcallback'      : (_opt_dlcallback_wrapper,   None                           ),
        'get_type'        : (_opt_type_wrapper,         C.GLYR_GET_UNSURE              ),
        'artist'          : (C.glyr_opt_artist,         None                           ),
        'album'           : (C.glyr_opt_album,          None                           ),
        'title'           : (C.glyr_opt_title,          None                           ),
        'img_minsize'     : (C.glyr_opt_img_minsize,    C.GLYR_DEFAULT_CMINSIZE        ),
        'img_maxsize'     : (C.glyr_opt_img_maxsize,    C.GLYR_DEFAULT_CMAXSIZE        ),
        'parallel'        : (C.glyr_opt_parallel,       C.GLYR_DEFAULT_PARALLEL        ),
        'timeout'         : (C.glyr_opt_timeout,        C.GLYR_DEFAULT_TIMEOUT         ),
        'redirects'       : (C.glyr_opt_redirects,      C.GLYR_DEFAULT_REDIRECTS       ),
        'useragent'       : (C.glyr_opt_useragent,      C.GLYR_SWIG_USERAGENT          ),
        'lang'            : (C.glyr_opt_lang,           C.GLYR_DEFAULT_LANG            ),
        'lang_aware_only' : (C.glyr_opt_lang_aware_only,False                          ),
        'number'          : (C.glyr_opt_number,         C.GLYR_DEFAULT_NUMBER          ),
        'verbosity'       : (C.glyr_opt_verbosity,      C.GLYR_DEFAULT_VERBOSITY       ),
        'from'            : (C.glyr_opt_from,           C.GLYR_DEFAULT_FROM            ),
        'plugmax'         : (C.glyr_opt_plugmax,        C.GLYR_DEFAULT_PLUGMAX         ),
        'allowed_formats' : (C.glyr_opt_allowed_formats,C.GLYR_DEFAULT_ALLOWED_FORMATS ),
        'download'        : (C.glyr_opt_download,       True                           ),
        'fuzzyness'       : (C.glyr_opt_fuzzyness,      C.GLYR_DEFAULT_FUZZYNESS       ),
        'qsratio'         : (C.glyr_opt_qsratio,        C.GLYR_DEFAULT_QSRATIO         ),
        'proxy'           : (C.glyr_opt_proxy,          None                           ),
        'force_utf8'      : (C.glyr_opt_force_utf8,     False                          ),
        'lookup_db'       : (C.glyr_opt_lookup_db,      None                           ),
        'db_autowrite'    : (C.glyr_opt_db_autowrite,   True                           ),
        'db_autoread'     : (C.glyr_opt_db_autoread,    True                           ),
        'musictree_path'  : (C.glyr_opt_musictree_path, None                           ),
}


def _dl_callback_proxy(cache, query, callback):
    c = Cache(cobj = cache)
    q = Query(cobj = query)
    rc = callback(q, c)
    if rc == None:
        return 0
    else:
        return rc

class Query(object):
    """
    Query resembles GlyrQuery in the C-API
    """
    def __init__(self,  cobj = None,  **kwargs):
        """
        Instance a new Query and call
        configure on it
        """
        if cobj == None:
            self.__query = C.GlyrQuery()
            C.glyr_query_init(self.__query)
            C.glyr_opt_verbosity(self.__query, 2)
            self.configure(**kwargs)
        else:
            self.__query = cobj 

    def __del__(self):
        """
        Free itself
        """
        self.__query.free()
 
    def __getattr__(self, name):
        try:
            return object.__getattribute__(self.__query,name)
        except AttributeError:
            print('No such attribute:', name)
        return None

    @property
    def cobj(self):
        """
        Return the underlying C-Structure
        """
        return self.__query

    def __set_opt(self, name, val):
        """
        Set a single glyr_opt()
        """
        try:
            OPT_DICT[name][0](self.__query, val)
        except KeyError: 
            print('Warning: No such option:', name)

    def default(self, name):
        """
        Lookup the Default for the option in name
        """
        try:
            return OPT_DICT[name][1]
        except KeyError: 
            print('Warning: No such option:', name)

        return None


    def configure(self,  **kwargs):
        """
        Set any option as available from the glyr_opt() family in C
        """
        for key in kwargs:
            self.__set_opt(key, kwargs[key])

    def clear(self):
        """
        Clear all previously set options, 
        and reset the query to it's defaults
        """
        C.glyr_query_destroy(self.__query)
        C.glyr_query_init(self.__query)

    def commit(self):
        """
        Start the configured job
        """
        # Do something very C-ish
        results = C.glyr_get(self.__query, None, None)
        return shared.linklist_to_list(results)


if __name__ == '__main__':
    def funny_smelling_callback(cache, query):
        """
        Example callback
        """
        print('<EXAMPLE CALLBACK>')
        print('Received:', cache.data)
        print('From Query:', query)
        print('</EXAMPLE CALLBACK>')
        return 0

    def main():
        """
        Testing main method
        """
        from database import Database
        db_conn = Database('/tmp')
        qry = Query(
                get_type   = 'lyrics',               # Get Lyrics
                artist     = 'Akrea',                # From artist Akrea
                title      = 'Trugbild',             # A nice song.
                lookup_db  = db_conn.cobj,           # Make item persistent
                dlcallback = funny_smelling_callback # Call a callback on find
                )

        print(qry.artist)
        qry.commit()
        del db_conn

        print(qry.default('from'))
        qry._from = 'Hello'
        print(qry._from)

    # Execute some testuse of the API
    main()
