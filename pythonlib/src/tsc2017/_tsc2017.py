#------------------------------------------------------------------------------
#   TrajTracker touchpad interface to the TSC2017 device
#------------------------------------------------------------------------------

from __future__ import division

import os
import ctypes
import numpy as np
import numbers


#-----------------------------------------------------------------
class TouchInfo(object):
    def __init__(self, touched, x, y):
        self.touched = touched
        self.x = x
        self.y = y


class TSCError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "{:}: {:}".format(type(self).__name__, self.message)


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
class DLLTouchInfo(ctypes.Structure):
    _fields_ = ("valid", ctypes.c_int), ("touched", ctypes.c_int), ("x", ctypes.c_float), ("y", ctypes.c_float)  #, ("z", ctypes.c_float)


#-----------------------------------------------------------------
def is_collection(value, allow_set=True):
    val_methods = dir(value)
    return "__len__" in val_methods and "__iter__" in val_methods and \
           (allow_set or "__getitem__" in val_methods) and not isinstance(value, str)


#-----------------------------------------------------------------
def is_coord(value, allow_float=False):
    elem_type = numbers.Number if allow_float else int
    return is_collection(value) and len(value) == 2 and \
           isinstance(value[0], elem_type) and isinstance(value[1], elem_type)

#=================================================================================================


touchpad_full_size = (4096, 4096)


class Touchpad(object):

    #------------------------------------------------------------
    def __init__(self, dll_path=None, scale_coords_by=None, shift_coords_by=None):
        """
        Initialize the Touchpad object.

        :param dll_path: The full path to the tsc_connect.dll file. If you do not have this file,
                         dowload it from `here <https://github.com/trajtracker/tsc2017/raw/master/lib/connect_dll.dll>`_
        :type dll_path: str

        :param scale_coords_by: See :attr:`~tsc2017.Touchpad.scale_coords_by`
        :param shift_coords_by: See :attr:`~tsc2017.Touchpad.shift_coords_by`
        """

        self._init_dll(dll_path)
        # noinspection PyUnresolvedReferences
        self._resource_manager = self._library.create_resource_manager()

        if self._resource_manager == 0:
            raise TSCError('Could not create a resource manager')

        self._resource = None
        self.scale_coords_by = scale_coords_by
        self.shift_coords_by = shift_coords_by

        self._last_touch_data = None

    #------------------------------------------------------------
    def __del__(self):
        if hasattr(self, "_resource"):
            self.disconnect()

        if hasattr(self, "_resource_manager") and ctypes is not None:   # ctypes may be None on program shutdown
            # noinspection PyUnresolvedReferences
            self._library.cleanup_resource_manager(ctypes.c_uint32(self._resource_manager))

    #------------------------------------------------------------
    def _init_dll(self, dll_path):

        if dll_path is None:
            dll_path = os.environ['WINDIR'] + "\\System\\"

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
                     ctypes.WINFUNCTYPE(DLLTouchInfo, ctypes.c_uint32),
                     ((1, "resource"), ))

        self._library = lib

    #=============================================================================================
    #     Configure properties
    #=============================================================================================

    #------------------------------------------------------------
    @property
    def scale_coords_by(self):
        """
        Scale the TSC2017-provided coordinates - multiply them by these factors.

        Scaling is done before applying :attr:`~tsc2017.Touchpad.shift_coords_by`

        :type: tuple (x scale, y scale)
        """
        return self._scale_coords_by

    @scale_coords_by.setter
    def scale_coords_by(self, value):
        if value is not None and not is_coord(value, allow_float=True):
            raise TypeError("{:}.scale_coords_by was set to an incorrect value ({:})".
                            format(type(self).__name__, value))
        self._scale_coords_by = value

    #------------------------------------------------------------
    @property
    def shift_coords_by(self):
        """
        Shift the TSC2017-provided coordinates - multiply them by these factors

        Shifting is done after applying :attr:`~tsc2017.Touchpad.scale_coords_by`, i.e., the shifts
        are specified in screen-pixel units

        :type: tuple (x shift, y shift)
        """
        return self._shift_coords_by

    @shift_coords_by.setter
    def shift_coords_by(self, value):
        if value is not None and not is_coord(value):
            raise TypeError("{:}.shift_coords_by was set to an incorrect value ({:})".
                            format(type(self).__name__, value))
        self._shift_coords_by = value

    #=============================================================================================
    #     Communicate with the TSC2017 touchpad
    #=============================================================================================

    #------------------------------------------------------------
    def connect(self, device_name):
        """
        Connect to a device.

        :param device_name: The USB device ID for the TSC2017 touchpad. Typically, this should be
                            "USB0::0x0451::0x2FD7::NI-VISA-30004::3::RAW", perhaps with a number other than
                            30004.

                            To get the device ID, run NI-MAX and check out the list of devices connected to your computer.
        :type device_name: str
        """
        if self._resource is not None:
            self.disconnect()

        # noinspection PyUnresolvedReferences
        resource = self._library.connect(ctypes.c_uint32(self._resource_manager), ctypes.c_char_p(device_name))
        if resource == 0:
            raise TSCError('Could not connect to device {:}'.format(device_name))

        self._resource = resource

    #------------------------------------------------------------
    def disconnect(self):
        """
        Disconnect from the TSC2017 device
        """
        if self._resource is not None:
            # noinspection PyUnresolvedReferences
            self._library.disconnect(ctypes.c_uint32(self._resource))
            self._resource = None

    #------------------------------------------------------------
    def get_touch_data(self):
        """
        Get touch data from the TSC2017 device.

        You must call :func:`~tsc2017.Touchpad.connect` before calling this function

        :return: tuple: (touched=bool, x=int, y=int)
        """

        if self._resource is None:
            raise TSCError("Invalid state: {:}.get_data() cannot be called before connect()".format(type(self).__name__))

        # noinspection PyUnresolvedReferences
        data = self._library.get_touch_info(ctypes.c_uint32(self._resource))

        if not data.valid:
            #-- No data available: get again the last available touch information
            if self._last_touch_data is None:
                return TouchInfo(False, 0, 0)

            data = self._last_touch_data

        #-- Get x, y coordinates, where (0, 0) is the center of the touchpad
        x = data.x - touchpad_full_size[0] / 2
        y = data.y - touchpad_full_size[1] / 2

        #-- Transform
        if self._scale_coords_by is not None:
            x *= self._scale_coords_by[0]
            y *= self._scale_coords_by[1]

        if self._shift_coords_by is not None:
            x += self._shift_coords_by[0]
            y += self._shift_coords_by[1]

        x = int(np.round(x))
        y = int(np.round(y))

        return TouchInfo(data.touched, x, y)
