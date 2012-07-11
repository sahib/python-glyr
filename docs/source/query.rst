Building Queries
================

A minimal Example
-----------------

Whenever you want to retrieve some metadata you use a Query: ::

    # A query understands lots of options, they can be either passed
    # on __init__ as keywords, or can be set afterwards as properties
    qry = Query(artist='Tenacious D', title='Deth Starr', get_type='lyrics')

    # Once a query is readily configured you can commit it
    # (you can even commit it more than once)
    items = qry.commit()

    # Well, great. Now we have one songtext. Since libglyr may return more than one item,
    # commit() always returns a list. The default value is 1 item though.
    # The list contains ,,Caches'', which are basically any sort of metadata.
    print(items[0].data)
    


Accessing Default Values
------------------------

Default Values for any option can be accessed by instantiating an empty Query,
and using the provided properties.

Reference
---------

.. autoclass:: plyr.Query
   :members:
