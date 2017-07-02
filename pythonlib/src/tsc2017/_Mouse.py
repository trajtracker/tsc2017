
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
        data = self._touchpad.get_data()
        return data[0]

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
        touched, x, y = self._touchpad.get_data()
        if touched:
            return x, y
        else:
            return 0, 0
