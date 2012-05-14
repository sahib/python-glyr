#!/usr/bin/env python
# encoding: utf-8
import cglyr as C
from shared import Property

class Cache(object):
    """
    Cache represents a single item from a Query.
    """
    def __init__(self,  cobj = None):
        if cobj == None: 
            self.__cache = C.glyr_cache_new()
        else:
            self.__cache = cobj
 
    def __repr__(self):
        # TODO: Own formatting needed
        C.glyr_cache_print(self.__cache)
        return ""

    def __len__(self):
        return self.size

    def __del__(self):
        self.__cache.free()
    
    @Property
    def cobj():
        """Set the cobj of this Item"""
        def fget(self):
            return self.__cache
    
    def write(self, path):
        """ 
        Write cache data to path
        Returns: Written Bytes
        """
        return C.glyr_cache_write(self.__cache, path)

    @Property
    def data():
        """Set the data of this Item"""
        def fget(self):
            return self.__cache.get_byte_array()
        def fset(self, byte_array):
            self.__cache.set_byte_array(byte_array)

    @Property
    def size():
        """Set the Size in Bytes of this Item"""
        def fget(self):
            return self.__cache.size
        def fset(self, val):
            self.__cache.size = val

    @Property
    def source_url():
        """Set the dsrc of this Item"""
        def fget(self):
            return self.__cache.dsrc
        def fset(self, val):
            C.glyr_cache_set_dsrc(self.__cache, val)

    @Property
    def provider():
        """Set the provider of this Item"""
        def fget(self):
            return self.__cache.prov
        def fset(self, val):
            C.glyr_cache_set_prov(self.__cache, val)

    @Property
    def data_type():
        """Set the data_type of this Item"""
        def fget(self):
            return C.glyr_data_type_to_string(self.__cache.type)
        def fset(self, type_str):
            type_id = C.glyr_string_to_data_type(type_str)
            C.glyr_cache_set_type(self.__cache, type_id)        

    @Property
    def duration():
        """Set the duration of this Item"""
        def fget(self):
            return self.__cache.duration
        def fset(self, val):
            self.__cache.duration = val   

    @Property
    def rating():
        """Set the rating of this Item"""
        def fget(self):
            return self.__cache.rating
        def fset(self, new_rating):
            C.glyr_cache_set_rating(self.__cache, new_rating)

    @Property
    def is_image():
        """Set the is_image of this Item"""
        def fget(self):
            return self.__cache.is_image
        def fset(self, val):
            self.__cache.is_image = val 

    @Property
    def image_format():
        """Set the image_format of this Item"""
        def fget(self):
            return self.__cache.img_format
        def fset(self, img_format):
            C.glyr_cache_set_img_format(self.__cache, img_format)

    @Property
    def md5sum():
        """Set the md5sum of this Item"""
        def fget(self):
            return C.glyr_md5sum_to_string(self.__cache.md5sum) 
        def fset(self, cksum_str):
            C.glyr_string_to_md5sum(cksum_str, self.__cache.md5sum)

    @Property
    def is_cached():
        """Set the is_cached of this Item"""
        def fget(self):
            return self.__cache.cached
        def fset(self, val):
            self.__cache.cached = val 

    @Property
    def timestamp():
        """Set the timestamp of this Item"""
        def fget(self):
            return self.__cache.timestamp
        def fset(self, val):
            self.__cache.timestamp = val   


if __name__ == '__main__':
    mycache = Cache()
    mycache.data_type = 'songtext'
    mycache.data_type = mycache.data_type

    mycache.duration = 100
    mycache.duration = mycache.duration

    mycache.is_image = False 
    mycache.is_image = mycache.is_image

    mycache.source_url = "MySite.yo"
    mycache.source_url = mycache.source_url

    mycache.data = bytearray([49, 50, 51]) 
    mycache.data = mycache.data
    mycache.data = bytearray([49, 50, 51]) 

    mycache.provider = "last.fm"
    mycache.provider = mycache.provider

    mycache.is_cached = True
    mycache.is_cached = mycache.is_cached

    mycache.timestamp = 1000.1
    mycache.timestamp = mycache.timestamp

    mycache.rating = 1
    mycache.rating = mycache.rating

    mycache.size = mycache.size

    print(mycache)
    print(mycache.data)
    mycache.md5sum = 'ffffffffffffffffffffffffffffffff'
    mycache.md5sum = mycache.md5sum
    print(mycache.md5sum)
    mycache.write('/tmp/test_cache')
