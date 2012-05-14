#!/usr/bin/env python
# encoding: utf-8   
import cglyr as C
import shared

class Database(object):
    def __init__(self, db_path = '', cobj = None):
        if cobj == None:
            self.__db = C.glyr_db_init(db_path)
        else:
            self.__db = cobj
 
    def __del__(self):
        self.__db.free()

    @property
    def cobj(self):
        return self.__db

    def lookup(self,query):
        results = C.glyr_db_lookup(self.cobj,query.cobj)
        return shared.linklist_to_list(results)

        
if __name__ == '__main__':
    from query import Query
    q = Query(get_type = 'cover', artist = 'Akrea', album = 'Lebenslinie') 

    db = Database('/tmp')
    print(db.lookup(q))

    db.close()
