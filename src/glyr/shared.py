#!/usr/bin/env python
#encoding: utf-8

import sys

# Recipe taken from:
# http://code.activestate.com/recipes/410698-property-decorator-for-python-24/
def Property(function):
    """
    A nicer way to implement getter/setter pairs than the 
    standard property() function
    """
    keys = 'fget',  'fset',  'fdel'
    func_locals = {'doc':function.__doc__}
    def probeFunc(frame,  event, arg):
        if event == 'return':
            c_locals = frame.f_locals
            func_locals.update(dict((k, c_locals.get(k)) for k in keys))
            sys.settrace(None)
        return probeFunc
    sys.settrace(probeFunc)
    function()
    return property(**func_locals)   

def linklist_to_list(head):
    """
    Convert a C-ish linked list to a python []
    GlyrMemCache has a 'next' attribute, which
    references the next Cache, in Line.
    """
    rlist = []
    if hasattr(head,'next'):
        nodeptr = head
        while nodeptr:
            rlist.append(nodeptr)
            nodeptr = nodeptr.next
    return rlist
