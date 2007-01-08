#!/usr/bin/python

#######################################################################################
#
#   Copyright (c) 2006 Loyola University Chicago and Contributors. All rights reserved.
#   This file is part of The Hydra Filesystem.
#
#   The Hydra Filesystem is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   The Hydra Filesystem is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with the Hydra Filesystem; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
#######################################################################################


import threading

#ref: http://www.zefhemel.com/archives/2005/01/02/python-beauty
    
import types

def _get_method_names (obj):
    from types import InstanceType, ObjectType
    from types import ClassType, TypeType
    from types import FunctionType, MethodType

    if  isinstance(obj, ObjectType):
      if isinstance(obj, InstanceType ):
        return _get_method_names(obj.__class__)
      elif isinstance(obj, TypeType)or isinstance(obj, ClassType):
        result = []
        for name, func in obj.__dict__.items():
            if isinstance(func, FunctionType) or isinstance(func, MethodType):
                result.append((name, func))
        for base in obj.__bases__:
            result.extend(_get_method_names(base))
        return result
      else:
        return _get_method_names(obj.__class__)
    else:
      raise TypeError, 'Invalid type'
"""
def _get_method_names(obj):
    "" Get all methods of a class or instance, inherited or otherwise. ""
    if type(obj) == types.InstanceType:
        return _get_method_names(obj.__class__)
    elif type(obj) == types.ClassType:
        result = []
        for name, func in obj.__dict__.items(  ):
            if type(func) == types.FunctionType:
                result.append((name, func))
        for base in obj.__bases__:
            result.extend(_get_method_names(base))
        return result
"""

class _SynchronizedMethod:
    """ Wrap lock and release operations around a method call. """

    def __init__(self, method, obj, lock):
        self.__method = method
        self.__obj = obj
        self.__lock = lock

    def __call__(self, *args, **kwargs):
        self.__lock.acquire( )
        try:
            return self.__method(self.__obj, *args, **kwargs)
        finally:
            self.__lock.release()


class SynchronizedObject:
    """ Wrap all methods of an object into _SynchronizedMethod instances. """

    def __init__(self, obj, ignore=[], lock=None):
        import threading

        # You must access _ _dict_ _ directly to avoid tickling _ _setattr_ _
        self.__dict__['_SynchronizedObject__methods'] = {}
        self.__dict__['_SynchronizedObject__obj'] = obj
        
        if not lock:
            lock = threading.RLock()
            
        for name, method in _get_method_names(obj):
            if not name in ignore and not self.__methods.has_key(name):
                self.__methods[name] = _SynchronizedMethod(method, obj, lock)

    def __getattr__(self, name):
        try:
            return self.__methods[name]
        except KeyError:
            return getattr(self.__obj, name)

    def __setattr__(self, name, value):
        setattr(self.__obj, name, value)

    
if __name__ == '__main__':
    import threading
    import time

    class Dummy:

            
        def foo (self):
            print 'hello from foo'
            time.sleep(1)

        def bar (self):
            print 'hello from bar'

        def baaz (self):
            print 'hello from baaz'

    tw = SynchronizedObject(Dummy(  ))
#    tw = Dummy()
    threading.Thread(target=tw.foo).start(  )
    time.sleep(.1)
    threading.Thread(target=tw.bar).start(  )
    time.sleep(.1)
    threading.Thread(target=tw.baaz).start(  )
