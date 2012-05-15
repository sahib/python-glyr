#!/usr/bin/env python
# encoding: utf-8
"""
Query Module
Send actual queries to libglyr
"""
import cglyr as C
import shared

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
    type_id = _lookup_type_from_string(type_str)
    C.glyr_opt_type(query, type_id)

OPT_DICT = {
        'dlcallback'      : C.glyr_opt_pycallback,      
        'get_type'        : _opt_type_wrapper,          
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
        'musictree_path'  : C.glyr_opt_musictree_path,  
}


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
            OPT_DICT[name](self.__query, val)
        except KeyError: 
            print('Warning: No such option:', name)

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

    main()
