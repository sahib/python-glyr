Salve te Wanderer!
==================

What is this about?
-------------------

This is the documentation to **plyr**, a Wrapper around **libglyr**, a library for finding and downloading
all sort of music-related metadata from a collection of providers. It's written in C and therefore available 
for musicplayers written directly in that language, or for programs that used the commandline interface **glyrc**.

Useful links
------------

**libglyr:**
    
    https://github.com/sahib/glyr 

**libglyr's API doc:**

    http://sahib.github.com/glyr/doc/html/index.html

**plyr on github:**

    https://github.com/sahib/python-glyr

**plyr on PyPI:**

    http://pypi.python.org/pypi/plyr

Installing
----------

**Using PyPI:**

  Use *pip* to install the package from source: ::

    sudo pip install plyr


**Manual Installation (most recent):**

  Install libglyr if not done yet. Either..
  
  - ... compile from Source: https://github.com/sahib/glyr/wiki/Compiling
  - ... or use the package your distribution provides.
  - ... in doubt, compile yourself. I only test the latest version.
  
      
  Install *cython* if not done yet: ::
  
     sudo pip install cython
  
  Build & install the Wrapper: ::
  
     git clone git://github.com/sahib/python-glyr.git
     cd python-glyr
     sudo python setup.py install
  
Documentation?
--------------

Silly question. You're looking at it. 
But when we're on it: There are only a few chapters, since there
is not so much to cover. Every chapter is split into a description,
and a reference. After all those theory chapters you are going to be rewarded
by some practical examples.

Please have *fun*.

Other things to note?
---------------------

Please use a own useragent, if you integrate glyr into your application.
You can set it via: :: 

  qry.useragent = 'projectname/ver.si.on +(https://project.site)'

Why? In case your application makes strange things and causes heavy traffic on
the provider's sites, they may ban the user-agent that makes this requests.
So, only your project gets (temporarly) banned, and not all libglyr itself.

TODOs:
------

- Finish libglyr; clean up API -> may break this here. (*sigh*!)
- Make a Provider Test-table, and replace the old ruby tests with that. (There be dragons).
