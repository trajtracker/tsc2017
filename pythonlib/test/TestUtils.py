
import tsc2017
from tsc2017._tsc2017 import TouchInfo


class _DummyTouchpadLib(object):
    pass


class TestTouchpad(tsc2017.Touchpad):

    #---------------------------------------------------------
    def __init__(self, reverse_left_right=False, reverse_up_down=False):
        super(TestTouchpad, self).__init__(reverse_left_right=reverse_left_right, reverse_up_down=reverse_up_down)
        self.data = False, 0, 0


    #---------------------------------------------------------
    def _init_dll(self, dll_path=""):

        self._library = _DummyTouchpadLib()
        self._library.create_resource_manager = lambda: 1
        self._library.cleanup_resource_manager = lambda: 0
        self._library.connect = lambda res_mgr, device_name: 1
        self._library.disconnect = lambda: 0
        self._library.get_touch_info = lambda resource: self._get_touch_info_impl()


    def _get_touch_info_impl(self):
        ti = TouchInfo()
        ti.touched = self._data[0]
        ti.x = self._data[1]
        ti.y = self._data[2]
        return ti


    #-------------------------------------------------------
    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        if not isinstance(value, (list, tuple)) or len(value) != 3 or \
            not isinstance(value[0], bool) or not isinstance(value[1], int) or not isinstance(value[2], int):
            raise TypeError("Invalida data")
        self._data = value
