#------------------------------------------------------------------------------
#   TrajTracker touchpad interface to the TSC2017 device
#------------------------------------------------------------------------------

from __future__ import division

import os
import ctypes
import numpy as np


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


def is_collection(value, allow_set=True):
    val_methods = dir(value)
    return "__len__" in val_methods and "__iter__" in val_methods and \
           (allow_set or "__getitem__" in val_methods) and not isinstance(value, str)


def is_coord(value):
    return is_collection(value) and len(value) == 2 and \
           isinstance(value[0], int) and isinstance(value[1], int)


#=================================================================================================

class Touchpad(object):
    """
    Get touch data from the TSC2017 touchpad, and optionally transform the coordinates to a different coordinate
    space.
    """

    #------------------------------------------------------------
    def __init__(self, dll_path=_default_dll_path,
                 reverse_left_right=False, reverse_up_down=False,
                 output_center=(0, 0), output_screen_size=None):
        """
        Initialize the Touchpad object.

        :param dll_path: The full path to the tsc_connect.dll file. If you do not have this file,
                         dowload it from `here <https://github.com/trajtracker/tsc2017/raw/master/lib/connect_dll.dll>`_
        :type dll_path: str

        :param reverse_left_right: Whether to reverse the TSC2017-provided coordinates horizontally
        :type reverse_left_right: bool

        :param reverse_up_down: Whether to reverse the TSC2017-provided coordinates vertically
        :type reverse_up_down: bool
        """

        self._init_dll(dll_path)
        # noinspection PyUnresolvedReferences
        self._resource_manager = self._library.create_resource_manager()

        if self._resource_manager == 0:
            raise Exception('Could not create a resource manager')

        self._resource = None
        self.reverse_left_right = reverse_left_right
        self.reverse_up_down = reverse_up_down
        self.output_center = output_center
        self.output_screen_size = output_screen_size

    #------------------------------------------------------------
    def __del__(self):
        if hasattr(self, "_resource"):
            self.disconnect()

        if hasattr(self, "_resource_manager"):
            # noinspection PyUnresolvedReferences
            self._library.cleanup_resource_manager(ctypes.c_uint32(self._resource_manager))

    #------------------------------------------------------------
    def _init_dll(self, dll_path=_default_dll_path):

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

    #=============================================================================================
    #     Configure properties
    #=============================================================================================

    #------------------------------------------------------------
    @property
    def reverse_left_right(self):
        """
        Whether to reverse the TSC2017-provided coordinates horizontally

        :type: bool
        """
        return self._reverse_left_right

    @reverse_left_right.setter
    def reverse_left_right(self, value):
        if not isinstance(value, bool):
            raise TypeError("{:}.reverse_left_right was set to an incorrect value ({:})".
                            format(type(self).__name__, value))
        self._reverse_left_right = value

    #------------------------------------------------------------
    @property
    def reverse_up_down(self):
        """
        Whether to reverse the TSC2017-provided coordinates vertically

        :type: bool
        """
        return self._reverse_up_down

    @reverse_up_down.setter
    def reverse_up_down(self, value):
        if not isinstance(value, bool):
            raise TypeError("{:}.reverse_up_down was set to an incorrect value ({:})".
                            format(type(self).__name__, value))
        self._reverse_up_down = value

    #------------------------------------------------------------
    @property
    def output_center(self):
        """
        This attribute controls the coordinate space returned by :func:`~tsc2017.Touchpad.get_data` :
        it defines the coordinate corresponding with the center of the touchpad

        :type: tuple (x, y)
        """
        return self.output_center

    @output_center.setter
    def output_center(self, value):
        if not is_coord(value):
            raise TypeError("{:}.output_center was set to incorrect value: {:}".format(type(self).__name__, value))
        self._output_center = value

    #------------------------------------------------------------
    @property
    def output_screen_size(self):
        """
        This attribute controls the coordinate space returned by :func:`~tsc2017.Touchpad.get_data` :
        it defines the size of the virtual screen (returned by get_data()) corresponding with the full touchpad area

        :type: tuple (width, height)
        """
        return self.output_screen_size

    @output_screen_size.setter
    def output_screen_size(self, value):
        if value is not None and not is_coord(value):
            raise TypeError("{:}.output_screen_size was set to incorrect value: {:}".format(type(self).__name__, value))
        self._output_screen_size = value

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
            raise Exception('Could not connect to device {:}'.format(device_name))

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
    def get_data(self):
        """
        Get touch data from the TSC2017 device.

        You must call :func:`~tsc2017.Touchpad.connect` before calling this function

        :return: tuple: (touched=bool, x=int, y=int)
        """

        if self._resource is None:
            raise Exception("Invalid state: {:}.get_data() cannot be called before connect()".format(type(self).__name__))

        # noinspection PyUnresolvedReferences
        data = self._library.get_touch_info(ctypes.c_uint32(self._resource))

        #-- Get x, y coordinates, where (0, 0) is the center of the touchpad
        x = int(np.round(data.x - self.touchpad_x_resolution() / 2))
        y = int(np.round(data.y - self.touchpad_y_resolution() / 2))

        #-- Flip if needed
        x = -x if self._reverse_left_right else x
        y = -y if self._reverse_up_down else y

        #-- Move to required center
        x += self._output_center[0]
        y += self._output_center[1]

        #-- Rescale
        if self._output_screen_size is not None:
            x = int(x * self._output_screen_size[0] / self.touchpad_x_resolution())
            y = int(y * self._output_screen_size[1] / self.touchpad_y_resolution())

        return data.touched, x, y

    #------------------------------------------------------------
    def touchpad_x_resolution(self):
        return 4096

    def touchpad_y_resolution(self):
        return 4096
