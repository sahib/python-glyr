Looking up Providers
====================

``plyr.PROVIDERS`` contains a nested dict modelling all compiled in fetchers and providers.

.. code-block:: python

   'albumlist': {
               'optional' : ('album', 'title'),
               'required' : ('artist'),
               'provider' : [{
                      'key'     : 'm',
                      'name'    : 'musicbrainz',
                      'quality' : 95,
                      'speed'   : 95
               },
               {
                      ... next_provider ...
               }]
   },
   'lyrics': {
        ... next_fetcher ...
   }

You can use this for example to get a list of all fetchers: ::

   list(plyr.PROVIDERS.keys())

You get the idea. Use ``itertools`` and friends to get the data you want in a oneliner.

.. note:: 

   This dictionary gets built on import.
