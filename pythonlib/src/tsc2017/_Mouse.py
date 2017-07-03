
from tsc2017 import Touchpad


class Mouse(object):

    #----------------------------------------------------------------
    def __init__(self, touchpad, ttrk_mouse=None):
        """
        Create a Mouse object

        :param touchpad:
        :type touchpad: Touchpad

        :param ttrk_mouse: The original "Mouse" object (`trajtracker.env.mouse <http://trajtracker.com/apiref/ttrk/Environment.html#trajtracker.Environment.mouse>`_)
        """
        if not isinstance(touchpad, Touchpad):
            raise TypeError("Invalid 'touchpad' argument - expecting a tsc2017.Touchpad object")
        if ttrk_mouse is None:
            raise TypeError("The 'ttrk_mouse' is None. You should initialize the TSC2017 as mouse only after calling trajtracker.initialize()")
        self._touchpad = touchpad
        self._ttrk_mouse = ttrk_mouse

    #----------------------------------------------------------------
    def check_button_pressed(self, button_number):
        """
        Check whether the finger is currently touching the touchpad

        :param button_number: Only 0 is supported
        :return: int
        """
        if button_number != 0:
            raise ValueError("tsc2017.{:}.check_button_pressed() got invalid button_number ({:}), only button #0 is supported".
                             format(type(self).__name__, button_number))
        return self._touchpad.get_touch_data().touched

    #----------------------------------------------------------------
    def show_cursor(self, show):
        """
        Show/hide the mouse pointer

        :param show:
        :type show: bool
        """
        if self._ttrk_mouse is not None:
            self._ttrk_mouse.show_cursor(show)

    #-----------------------------------------------------
    @property
    def position(self):
        """
        Get the current position of the finger on the touchpad

        :return: (x, y) coordinates
        """
        ti = self._touchpad.get_touch_data()
        if ti.touched:
            return ti.x, ti.y
        else:
            return 0, 0
