
import os
from tsc2017 import TouchInfo, TSCError



#---------------------------------------------------------------------------
class TouchpadMouseSimulator(object):
    """
    Uses the mouse to emulate the TSC2017 behavior
    """

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


#---------------------------------------------------------------------------
# Get the path to CONNECT_TSC.DLL
#
def get_dll_path():
    while True:
        dll_path = raw_input("Enter the path to CONNECT_TSC.DLL: ")
        if os.path.isdir(dll_path):
            return dll_path
        elif os.path.isfile(dll_path):
            print("Please indicate the directory name, not a file name.")
        else:
            print("Directory does not exist. Try again.")


#---------------------------------------------------------------------------
def connect_to_device(touchpad):

    print("")
    print("The USB device ID (which you can see in the NI-MAX application) should be")
    print("USB0::0x0451::0x2FD7::NI-VISA-#####::3::RAW, where '#####' is a sequence of digits")

    while True:
        device_id_num = raw_input("Please type this digit sequence:")
        device_id = "USB0::0x0451::0x2FD7::NI-VISA-{:}::3::RAW".format(device_id_num)
        print("Trying to connect to {:}".format(device_id))
        try:
            touchpad.connect(device_id)
            print("Succeeded")
            return device_id
        except TSCError:
            print("Cannot connect to this device. Please double-check and try again.")


