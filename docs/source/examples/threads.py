#!/usr/bin/env python
# -*- coding: utf-8 -*-

import plyr
import random
from time import sleep
from threading import Thread

"""
Example on how to use the cancel() function of the Query.

If a Query has been started it wil block the calling thread.
This may be bad, when you want to do something different in the meantime.
You can safely run qry.commit() in a seperate thread and do some data-sharing.
But sometimes (e.g. on application exit) you may want to stop all running queries.
This can be done via the cancel() function - it will stop all running downloads
associated with this query.

There is no cancel_all() function. You gonna need a pool with all Queries you're running.

Note: cancel() will not stop __imediately__, since some provider may do some
      stuff that is hard to interrupt, but at least you do not need to care about cleanup.
"""

if __name__ == '__main__':
    # Some real query, that may take a bit longer
    # Notice this nice unicode support :-)
    qry = plyr.Query(artist='Аркона', title='Гой Роде Гой!', get_type='lyrics')

    # Our worker thread
    def cancel_worker():
        sleep(random.randrange(1, 4))
        print('cancel()')
        qry.cancel()

    # Spawn the thread.
    Thread(target=cancel_worker).start()

    # Start the query, and let's see.
    print('commit() started')
    items = qry.commit()
    print('commit() finished')
    print('Number of results:', len(items))

    # Print if any item was there, there shouldn't be any.
    if len(items) > 0:
        print(str(items[0].data, 'UTF-8'))
