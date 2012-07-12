#!/usr/bin/env python
# -*- coding: utf-8 -*-

import plyr


def on_item_received(cache, query):
    cache.print_cache()


if __name__ == '__main__':
    # Use a local db
    db = plyr.Database('/tmp')

    # Create a Query, so plyr knows what you want to search
    qry = plyr.Query(
            get_type='lyrics',
            artist='Tenacious D',
            title='Deth Starr',
            callback=on_item_received,
            verbosity=3,
            database=db)

    # Now let it search all the providers
    # Even with callback, it will return a list of caches
    qry.commit()
