#include <Python.h>

static PyObject* hello(PyObject *self, PyObject *args)
{
  printf("Hello, world!");
  Py_RETURN_NONE;
}

static PyMethodDef module_methods[] = {
  { "hello", (PyCFunction)hello, METH_NOARGS, NULL},
  {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initHello() {
  Py_InitModule3("Hello", module_methods, "An example python C module...");
}
