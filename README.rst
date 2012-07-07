Plyr - A Wrapper around libglyr, using Cython
=============================================

Not much to see yet, documentation will be on readthedocs_.

.. _readthedocs: http://plyr.readthedocs.org/en/latest/

Installing
----------

.. code-block:: bash
  $ python setup.py build_ext --inplace --force

.. code-block:: python
  import plyr
  q = plyr.Query(artist='Akrea', album='Lebenslinie', get_type='cover')
  q.commit()
