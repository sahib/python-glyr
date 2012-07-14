#!/usr/bin/env python
# -*- coding: utf-8 -*-

import plyr


# This is called on each item found in the db
# The query is the search-query used to search this
# item, with artist, album and title filled.
# The query is useful to do delete or insert operations
# cache is the actual item, with all data filled.
def foreach_callback(query, cache):
    print(query)
    cache.print_cache()


if __name__ == '__main__':
    db = plyr.Database('/tmp')

    # Insert at least one dummy item, just in case the db is empty et
    # This will grow on each execution by one item.
    dummy_qry = plyr.Query(artist='Derp', album='Derpson', get_type='cover')
    dummy_itm = db.make_dummy()
    db.insert(dummy_qry, dummy_itm)

    # Now iterate over all items in the db
    # and exit afterwards
    db.foreach(foreach_callback)
