/*
 * This is the config file for SWIG, the binding generator for a plethora of languages
 * Only thing not working right now:
 * glyr_opt_dlcallback() - as it requires some C-ruby magic to get it to work.
*/
 
/* module name */
%module cglyr 

/* let wrapper file compile */
%runtime %{ 
#include <glyr/glyr.h>    
#include <glyr/cache.h>   
#include <glyr/testing.h> 
#include <glyr/misc.h>    
%}

/* parse headers */
%include <glyr/glyr.h>
%include <glyr/types.h>
%include <glyr/cache.h>
%include <glyr/config.h>
%include <glyr/testing.h>
%include <glyr/misc.h>

//////////////////////////

// ----------------------------------------------------------------
// Handling of binary data (currently by using a bytearray in Python3)
// ----------------------------------------------------------------

%runtime %{
    PyObject * byte_array_from_cache(GlyrMemCache * cache) 
    {
        if(cache == NULL)
            return NULL;

#if PY_MAJOR_VERSION >= 3
        return PyByteArray_FromStringAndSize(cache->data,cache->size);
#else
        return PyBuffer_FromMemory(cache->data,cache->size);
#endif
    }
%}

//////////////////////////

%extend GlyrMemCache {
    PyObject * byte_array() {
        return byte_array_from_cache($self);
    }
};

//////////////////////////
           
// -------------------------------------------------------------------
// SWIG typemap allowing us to grab a Python callable object
// -------------------------------------------------------------------

%typemap(in) PyObject *PyFunc {
  if (!PyCallable_Check($input)) {
      PyErr_SetString(PyExc_TypeError, "Need a callable object!");
      return NULL;
  }
  $1 = $input;
}

/*
 * Our new python callback registration function.  Note the use of 
 * a typemap to grab a PyObject.
 */
void glyr_opt_pycallback(GlyrQuery * q, PyObject *PyFunc);
                                                                

// ----------------------------------------------------------------
// Python helper functions for adding callbacks
// Based on: http://www.fifi.org/doc/swig-examples/python/callback/widget.i 
// ----------------------------------------------------------------

%runtime %{
    /* Prototype */
    static GLYR_ERROR PythonCallBack(GlyrMemCache * c, GlyrQuery * q);

    /* Callback Setter */
    static void glyr_opt_pycallback(GlyrQuery * q, PyObject * PyFunc) {
      glyr_opt_dlcallback(q,PythonCallBack, (void *) PyFunc);
      Py_INCREF(PyFunc);
    }
%}

//////////////////////////

%extend GlyrQuery {
    void register_callback(PyObject *PyFunc) {
        glyr_opt_pycallback($self,PyFunc);
    }
};

//////////////////////////

%inline %{
    /* This function matches the prototype of a normal C callback
       function for our widget. However, the clientdata pointer
       actually refers to a Python callable object. */
    static GLYR_ERROR PythonCallBack(GlyrMemCache * c, GlyrQuery * q)
    {
       PyObject * func, * arglist,
                * pycache, * pyquery,
                * result;
       long dres = 0;
       
       /*
        * This feels somewhat hackish, but works just fine.
        * Only Problem is that we rely that SWIG's method names
        * stay like this
        */
       func = (PyObject *) q->callback.user_pointer;
       pycache = SWIG_NewPointerObj(SWIG_as_voidptr(c), SWIGTYPE_p__GlyrMemCache, 0); 
       pyquery = SWIG_NewPointerObj(SWIG_as_voidptr(q), SWIGTYPE_p__GlyrQuery,    0); 

       arglist = Py_BuildValue("(OO)",pycache,pyquery);
       if(arglist == NULL)
           goto fail;

       result = PyEval_CallObject(func,arglist);
       Py_DECREF(arglist);

       if(result != NULL) {
         dres = PyLong_AsLong(result);
       }
       Py_XDECREF(result);
       return dres;

    fail:
       return 0;
    }
%}

//////////////////////////

// ----------------------------------------------------------------
// Initializazion stuff belongs here
// ----------------------------------------------------------------

%init 
%{
  glyr_init();
  atexit(glyr_cleanup);
%}
