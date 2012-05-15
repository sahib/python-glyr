/* Python bindings for libglyr - SWIG Interface file
 *
 * All API offered by libglyr is included here, plus 
 * additional helpers for use with byte-arrays and callbacks.
 *
 * This is Python3 only, Python2 would require some extra-work I think.
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
    /* Pack the data of a GlyrMemCache into an PyByteArray
     *
     * This is a wrapper around cache->data
     */
    PyObject * byte_array_from_cache(GlyrMemCache * cache) 
    {
        if(cache == NULL)
            return NULL;

        return PyByteArray_FromStringAndSize(cache->data,cache->size);
    }

    /* Set the content of an ByteArray to a GlyrMemCache
     * This involves no copying.
     *
     * This is a wrapper aroung glyr_cache_set_data()
     */
    void set_data_from_byte_array(GlyrMemCache * cache, PyObject * byteArr)
    {
        if(cache == NULL || byteArr == NULL)
            return;

        if(PyByteArray_Check(byteArr))
        {
            Py_INCREF(byteArr);
            glyr_cache_set_data(cache,PyByteArray_AsString(byteArr),PyByteArray_Size(byteArr));
        }
        else
        {
            fprintf(stderr,"set_data_from_byte_array: Passed object is not a valid ByteArray\n");
        }
    }
%}

//////////////////////////

/*
 * Our new python callback registration function.  Note the use of 
 * a typemap to grab a PyObject.
 */
void glyr_opt_pycallback(GlyrQuery * q, PyObject *PyFunc);
void glyr_db_foreach_pycallback(GlyrDatabase * db, PyObject *PyFunc);


/* 
 * Make above func-calls actually available
 */
%extend GlyrMemCache {
    PyObject * get_byte_array() {
        return byte_array_from_cache($self);
    }

    void set_byte_array(PyObject * byteArr) {
        set_data_from_byte_array($self,byteArr);
    }

    void free() {
        glyr_cache_free($self);
        $self = NULL;
    }
};

//////////////////////////

%extend GlyrQuery {
    void register_callback(PyObject *PyFunc) {
        glyr_opt_pycallback($self,PyFunc);
    }     

    void free() {
        glyr_query_destroy($self);
        $self = NULL;
    }
}

//////////////////////////

%extend GlyrDatabase {
    /* Handling raw md5sums may be painful in Python */
    void db_replace(const char * md5sum_str,
                    GlyrQuery * query, GlyrMemCache * cache) {
        unsigned char md5sum_buf[16];

        if(md5sum_str == NULL)
            return;
        puts(md5sum_str);

        glyr_string_to_md5sum(md5sum_str,md5sum_buf);
        glyr_db_replace($self,md5sum_buf, query, cache);
    }

    void foreach(PyObject *PyFunc) {
        glyr_db_foreach_pycallback($self,PyFunc);
    }

    void free() {
        glyr_db_destroy($self);
        $self = NULL;
    }
}

//////////////////////////

%extend GlyrFetcherInfo {
    void free() {
        glyr_info_free($self);
        $self = NULL;
    }
}

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

                                                                

// ----------------------------------------------------------------
// Python helper functions for adding callbacks
// Based on: http://www.fifi.org/doc/swig-examples/python/callback/widget.i 
// ----------------------------------------------------------------

%runtime %{
    /* Prototype */
    static GLYR_ERROR PythonDownloadCallback(GlyrMemCache * c, GlyrQuery * q);
    static int PythonDBForearchCallback(GlyrQuery * q, GlyrMemCache * c, void * userptr);

    /* Callback Setter for the Download callback */
    static void glyr_opt_pycallback(GlyrQuery * q, PyObject * PyFunc) {
      glyr_opt_dlcallback(q,PythonDownloadCallback, (void *) PyFunc);
      Py_INCREF(PyFunc);
    }

    /* Callback Setter for the Foreach callback */
    static void glyr_db_foreach_pycallback(GlyrDatabase * db, PyObject * PyFunc) {
        glyr_db_foreach(db,PythonDBForearchCallback, (void *) PyFunc);
        Py_INCREF(PyFunc);
    }
%}

//////////////////////////

%inline %{

    /* This function matches the prototype of a normal C callback
       function for our Query. However, the callback.user_pointer
       actually refers to a Python callable object. */
    static GLYR_ERROR PythonDownloadCallback(GlyrMemCache * c, GlyrQuery * q)
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

    static int PythonDBForearchCallback(GlyrQuery * q, GlyrMemCache * c, void * userptr) {
       PyObject * func = (PyObject *) userptr;
       PyObject * pycache, * pyquery, * result, * arglist;
       long dres = 0;

       pycache = SWIG_NewPointerObj(SWIG_as_voidptr(c), SWIGTYPE_p__GlyrMemCache, 0); 
       pyquery = SWIG_NewPointerObj(SWIG_as_voidptr(q), SWIGTYPE_p__GlyrQuery,    0); 

       arglist = Py_BuildValue("(OO)",pyquery,pycache);
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
  Py_INCREF(m);
%}
