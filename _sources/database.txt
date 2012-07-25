Using a Database to cache items locally
=======================================

Sometimes it's nice to have a local database that caches already downloaded items,
so they don't get downloaded over and over. This can be achieved quite easy: ::

  # Create a database in /tmp/metadata.db
  db = Database('/tmp/')

  # use it in queries
  qry = Query(database=db,
              artist='The Cranberries',
              title='Zombie',
              get_type='lyrics')

  ...

But what happenes if a item is not found? Nothing is written to the db,
and the next time it is requeried. Not always what you want. 
If you get an empty return from qry.commit() you could do the following: ::

  def insert_dummy(db, used_query):
      dummy = Database.make_dummy()
      db.insert(used_query, dummy)


On the next commit you will get this item instead of an empty return,
you can check for it via: ::

  if returned_cache.rating is -1:
     pass  # it's a dummy
  else:
     pass  # real item


Reference
---------

.. autoclass:: plyr.Database
   :members:
