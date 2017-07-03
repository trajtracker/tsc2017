
from tsc2017 import TouchInfo



class TouchpadMouseSimulator(object):

    def __init__(self, exp, ttrk_mouse):
        self._exp = exp
        self._mouse = ttrk_mouse

    def get_touch_data(self):
        touched = self._mouse.check_button_pressed(0)
        x, y = self._mouse.position
        return TouchInfo(touched, x, y)

    def touchpad_x_resolution(self):
        return self._exp.screen.size[0]

    def touchpad_y_resolution(self):
        return self._exp.screen.size[1]
