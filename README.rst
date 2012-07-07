Plyr - A Wrapper around libglyr, using Cython
=============================================

Not much to see yet, documentation will be on readthedocs_.

.. _readthedocs: http://plyr.readthedocs.org/en/latest/

Installing
----------

Building Cython module::
  
  $ sudo pip install cython # if not done yet
  $ python setup.py build_ext --inplace --force

Usage
-----

Probably not yet working example::

  import plyr
  q = plyr.Query(artist='Akrea', album='Lebenslinie', get_type='cover')
  q.commit()
