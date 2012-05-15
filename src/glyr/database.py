#!/usr/bin/env python
# encoding: utf-8   
import cglyr as C
import shared

from cache import Cache
from query import Query

class Database(object):
    def __init__(self,  db_path = '',  cobj = None):
        if cobj == None:
            self.__db = C.glyr_db_init(db_path)
        else:
            self.__db = cobj
 
    def __del__(self):
        self.__db.free()

    @property
    def cobj(self):
        return self.__db

    def lookup(self, query):
        results = C.glyr_db_lookup(self.cobj, query.cobj)
        return shared.linklist_to_list(results)

    def delete(self, query):
        return C.glyr_db_delete(self.cobj, query.cobj)

    def insert(self, query, cache):
        C.glyr_db_insert(self.cobj, query.cobj, cache.cobj)

    def edit(self, query, edited_cache):
        return C.glyr_db_edit(self.cobj,  query.cobj, edited_cache.obj)

    def replace(self, cksum_str, query, cache):
        self.__db.db_replace(cksum_str,query.cobj,cache.cobj)
        pass

    def foreach(self, func):
        self.__db.foreach(func)
    

if __name__ == '__main__':
    q = Query(get_type = 'cover',  artist = 'Akrea',  album = 'Lebenslinie') 

    db = Database('/tmp')
    
    def foreach_cb(query, cache):
        mc = Cache(cobj = cache, delete_struct = False)
        print('..... =>')
        print(mc)
        print('<= .....')
        return 0 # means: continue
     
    dummy_query = Query(get_type = 'lyrics', artist = 'Akrea', title = 'Trugbild')
    dummy_cache = Cache.make_dummy()
    dummy_cache.data = bytearray("Hello","UTF-8")
    
    db.insert(dummy_query,dummy_cache)

    db.foreach(foreach_cb)
    print('------------------')
    rc = db.replace(dummy_cache.md5sum, dummy_query, Cache.make_dummy()) 

    db.foreach(foreach_cb)

    db.delete(dummy_query)
    print('------------------')
    db.foreach(foreach_cb)
    print('------------------')
    del db
