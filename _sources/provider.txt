Looking up Providers
====================

``plyr.PROVIDERS`` contains a nested dict modelling all compiled in fetchers and providers.

.. code-block:: python

   'albumlist': {                                 # The name of this fetcher
               'required' : ('artist'),           # A list of required properties
               'optional' : (),                   # A list of properties that are optional
               'provider' : [{                    # A list of providers this fetcher can use
                      'key'     : 'm',            # one-char identifier of this provider (rarely used)
                      'name'    : 'musicbrainz',  # Full name of this provider
                      'quality' : 95,             # subjective quality (0/100)
                      'speed'   : 95              # subjective speed (0/100)
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

   This dictionary gets built on import. Different version of libglyr may
   deliver different providers.
