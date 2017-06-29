#------------------------------------------------------------------------------
#   TrajTracker touchpad interface to the TSC2017 device
#------------------------------------------------------------------------------

import numpy as np
import os
import ctypes


_default_dll_path = os.environ['WINDIR'] + "\\System\\"


#------------------------------------------------------------
class DLLFuncs(object):

    def __init__(self, dll, dll_path):
        self.dll = dll
        self.dll_path = dll_path

    def add_func(self, name_in_python, name_in_dll, prototype, params):
        func = prototype((name_in_dll, self.dll), params)
        setattr(self, name_in_python, func)


#-----------------------------------------------------------------
#-- The value returned from the DLL's get_touch_info() function
class TouchInfo(ctypes.Structure):
    _fields_ = ("touched", ctypes.c_int), ("x", ctypes.c_float), ("y", ctypes.c_float)  #, ("z", ctypes.c_float)



#=================================================================================================

class Touchpad(object):
    """
    Allow getting touch data from the TSC2017 touchpad
    """

    #------------------------------------------------------------
    def __init__(self, dll_path=_default_dll_path):

        self._init_dll(dll_path)
        # noinspection PyUnresolvedReferences
        self._resource_manager = self._library.create_resource_manager()

        if self._resource_manager == 0:
            raise Exception('Could not create a resource manager')

        self._resource = None


    #------------------------------------------------------------
    def __del__(self):
        if hasattr(self, "_resource"):
            self.disconnect()

        if hasattr(self, "_resource_manager"):
            # noinspection PyUnresolvedReferences
            self._library.cleanup_resource_manager(ctypes.c_uint32(self._resource_manager))


    #------------------------------------------------------------
    def _init_dll(self, dll_path=_default_dll_path):
        """
        Initialize the library. To set a certain DLL,
        """
        dll = ctypes.WinDLL(dll_path)

        lib = DLLFuncs(dll, dll_path)

        lib.add_func("create_resource_manager", "create_resource_manager",
                     ctypes.WINFUNCTYPE(ctypes.c_uint32),
                     ())

        lib.add_func("cleanup_resource_manager", "cleanup_resource_manager",
                     ctypes.WINFUNCTYPE(None, ctypes.c_uint32),
                     ((1, "resource_mgr"), ))

        lib.add_func("disconnect", "disconnect",
                     ctypes.WINFUNCTYPE(None, ctypes.c_uint32),
                     ((1, "resource"), ))

        lib.add_func("connect", "connect",
                     ctypes.WINFUNCTYPE(ctypes.c_uint32, ctypes.c_uint32, ctypes.c_char_p),
                     ((1, "resource_mgr"), (1, "resource_name")))

        lib.add_func("get_touch_info", "get_touch_info",
                     ctypes.WINFUNCTYPE(TouchInfo, ctypes.c_uint32),
                     ((1, "resource"), ))

        self._library = lib


    #------------------------------------------------------------
    def connect(self, device_name):

        # noinspection PyUnresolvedReferences
        resource = self._library.connect(ctypes.c_uint32(self._resource_manager), ctypes.c_char_p(device_name))
        if resource == 0:
            raise Exception('Could not connect to device {:}'.format(device_name))

        self._resource = resource


    #------------------------------------------------------------
    def disconnect(self):
        if self._resource is not None:
            # noinspection PyUnresolvedReferences
            self._library.disconnect(ctypes.c_uint32(self._resource))
            self._resource = None


    #------------------------------------------------------------
    def get_data(self):

        if self._resource is None:
            raise Exception("Invalid state: {:}.get_data() cannot be called before connect()".format(type(self).__name__))

        # noinspection PyUnresolvedReferences
        data = self._library.get_touch_info(ctypes.c_uint32(self._resource))

        return data
