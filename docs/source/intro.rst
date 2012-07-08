Salve te Wanderer!
==================

What is this about?
-------------------

This is the documentation to **plyr**, a Wrapper around **libglyr**, a library for finding and downloading
all sort of music-related metadata from a collection of providers. It's written in C and therefore available 
for musicplayers written directly in that language, or for programs that used the commandline interface **glyrc**.

libglyr: 
    
    https://github.com/sahib/glyr 

libglyr's API doc:

    http://sahib.github.com/glyr/doc/html/index.html


.. note::
   
   This Wrapper is beta-software. It may blow your computer totally unexcpted.

Installing
----------

Install *cython* if not done yet: ::

   sudo pip install cython

Build & install the Wrapper: ::

   git clone git://github.com/sahib/python-glyr.git
   cd python-glyr
   sudo python setup.py install
