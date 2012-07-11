Retrieved Items (aka ,,Caches'')
================================

What is a Cache?
----------------

Basically every single bit of metadata returned from **libglyr** is a Cache. 
It is basically a *result* or it is sometimes referred to as an item.
It encapsulates basic attributes like a bytearray of data,
a checksum, an optional imageformat and some more.

What can I do with one?
-----------------------

Caches can be...

- ... committed to a local database (see next section)
- ... written to HD via it's ``write()`` method.
- ... printed to stdout via ``print()``, currently ``__repr__`` is not implemented.


You can use the *data* property to get the actual metadata.
This is always a bytestring, even with lyrics. 
You have to convert it to the desired encoding (e.g. utf-8) like this: ::

  str(some_cache.data, 'utf-8')

.. note:: 

  This might throw an UnicodeError on non-utf8 input, or imagedata.
  Use the Query-Property **force_utf8** to only retrieve valid utf-8 textitems.


The *data* property is settable. Setting will also cause the size and checksum to be adjusted.


Reference
---------

.. autoclass:: plyr.Cache
   :members:
