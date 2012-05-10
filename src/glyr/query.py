#!/usr/bin/env python
# encoding: utf-8
import glyr.cglyr as C

def lookup_type_from_string(type_str):
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
                    
def opt_type_wrapper(query,type_str):
    type_id = lookup_type_from_string(type_str)
    C.glyr_opt_type(query,type_id)

opt_dict = {
        'dlcallback'      : C.glyr_opt_pycallback,
        'get_type'        : opt_type_wrapper,
        'artist'          : C.glyr_opt_artist,
        'album'           : C.glyr_opt_album,
        'title'           : C.glyr_opt_title,
        'img_minsize'     : C.glyr_opt_img_minsize,
        'img_maxsize'     : C.glyr_opt_img_maxsize,
        'parallel'        : C.glyr_opt_parallel,
        'timeout'         : C.glyr_opt_timeout,
        'redirects'       : C.glyr_opt_redirects,
        'useragent'       : C.glyr_opt_useragent,
        'lang'            : C.glyr_opt_lang,
        'lang_aware_only' : C.glyr_opt_lang_aware_only,
        'number'          : C.glyr_opt_number,
        'verbosity'       : C.glyr_opt_verbosity,
        'from'            : C.glyr_opt_from,
        'plugmax'         : C.glyr_opt_plugmax,
        'allowed_formats' : C.glyr_opt_allowed_formats,
        'download'        : C.glyr_opt_download,
        'fuzzyness'       : C.glyr_opt_fuzzyness,
        'qsratio'         : C.glyr_opt_qsratio,
        'proxy'           : C.glyr_opt_proxy,
        'force_utf8'      : C.glyr_opt_force_utf8,
        'lookup_db'       : C.glyr_opt_lookup_db,
        'db_autowrite'    : C.glyr_opt_db_autowrite,
        'db_autoread'     : C.glyr_opt_db_autoread,
        'musictree_path'  : C.glyr_opt_musictree_path
}


class Query:
    def __init__(self,**kwargs):
        """
        Instance a new Query and call
        configure on it
        """
        self.__query = C.GlyrQuery()
        C.glyr_query_init(self.__query)
        self.configure(**kwargs)

    def __set_opt(self,name,val):
        """
        Set a single glyr_opt()
        """
        try:
            opt_dict[name](self.__query,val)
        except: 
            pass

    def configure(self, **kwargs):
        """
        Set any option as available from the glyr_opt() family in C
        """
        for key in kwargs:
            self.__set_opt(key,kwargs[key])

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
        rlist = []

        # Do something very C-ish
        results = C.glyr_get(self.__query,None,None)
        nodeptr = results

        while nodeptr:
            rlist.append(nodeptr)
            nodeptr = nodeptr.next

        return rlist


def funny_smelling_callback(cache,query):
    print('Received:',cache.data)
    

if __name__ == '__main__':
    db = C.glyr_db_init('/tmp')
    q = Query(
            get_type   = 'lyrics', 
            artist     = 'Akrea',
            album      = 'Lebenslinie',
            title      = 'Trugbild',
            lookup_db  = db,
            dlcallback = funny_smelling_callback
            )

    mylist = q.commit()
    C.glyr_db_destroy(db)
