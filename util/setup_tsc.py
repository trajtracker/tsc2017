
from __future__ import division

import os
import random
import time
import sklearn.linear_model as lin

import expyriment as xpy
import trajtracker as ttrk

from tsc2017 import Touchpad
import setup_utils as sut


#============================================================================
#   To configure what this utility does
#============================================================================

#-- To simulate this app with mouse rather than with the real touchpad
simulate_with_mouse = False

n_pointings_per_quarter = 3


#---------------------------------------------------------------------------
def main():

    print("")
    print("-------------------------------------------------")
    print("     Establishing connection with TSC2017")
    print("-------------------------------------------------")
    print("")

    xpy.control.defaults.window_mode = True
    ttrk.log_to_console = True
    exp = ttrk.initialize()
    xpy.control.start(exp)

    if simulate_with_mouse:
        exp.mouse.show_cursor()
        touchpad = sut.TouchpadMouseSimulator(exp, ttrk.env.mouse)
        dll_path = "N/A"
        device_id = "N/A"

    else:
        dll_path = sut.get_dll_path()
        dll_path += "\\connect_tsc.dll"
        touchpad = Touchpad(dll_path)
        device_id = sut.connect_to_device(touchpad)

    target_positions = generate_positions()
    marked_positions = ask_to_mark(target_positions, touchpad)

    print("target = {:}".format(target_positions))
    print("marked = {:}".format(marked_positions))

    intercepts, scale_factors = get_scaling_factors(target_positions, marked_positions)

    save_script(dll_path, device_id, intercepts, scale_factors)

    xpy.control.end()


#---------------------------------------------------------------------------
def generate_positions():
    """
    Generate random positions to which the user will then point
    """
    width, height = ttrk.env.screen_size

    max_x = int(width * 0.4)  # don't get too far to the end of the scree
    min_x = int(max_x * 0.15)

    max_y = int(height * 0.4)
    min_y = int(max_y * 0.15)

    positions = []

    for xdir in (-1, 1):
        for ydir in (-1, 1):
            for i in range(n_pointings_per_quarter):
                x = random.randint(min_x, max_x)
                y = random.randint(min_y, max_y)
                positions.append((int(x * xdir), int(y * ydir)))

    return positions


#---------------------------------------------------------------------------
def ask_to_mark(target_positions, touchpad):

    marked_positions = []

    msg = xpy.stimuli.TextBox(text="Click the point", text_font="Arial", text_size=14, size=(200, 30), position=(0, 0))
    msg2 = xpy.stimuli.TextBox(text="Good!", text_font="Arial", text_size=14, size=(200, 30), position=(0, 0),
                               text_colour=xpy.misc.constants.C_GREEN)
    point = xpy.stimuli.Circle(radius=2, colour=xpy.misc.constants.C_WHITE)

    for i in range(len(target_positions)):

        msg.text = "Click the point ({:}/{:})".format(i+1, len(target_positions))
        print(msg.text)

        msg.present(update=False)

        point.position = target_positions[i]
        point.present(clear=False)

        while True:

            td = touchpad.get_touch_data()
            if td.touched:
                pos = (td.x, td.y)
                print("Displayed at {:}, touched at {:}".format(target_positions[i], pos))
                marked_positions.append(pos)
                msg2.present()

                #-- wait until finger lifted, plus a little longer
                if i+1 < len(target_positions):
                    while touchpad.get_touch_data().touched:
                        time.sleep(0.02)
                    time.sleep(0.5)

                break
            else:
                time.sleep(0.02)

            xpy.io.Keyboard.process_control_keys()

    msg2.text = "Thank you"
    msg.present()
    time.sleep(0.5)

    return marked_positions


#---------------------------------------------------------------------------
def get_scaling_factors(target_positions, marked_positions):
    """
    Compute how the marked coordinates should be scaled to match the target coordinates
    :return: tuple (intercepts, scales): each of the two is a tuple with 2 elements (x, y)
    """

    regression = lin.LinearRegression()
    intercepts = []
    scales = []

    for coord in 0, 1:

        target = [c[coord] for c in target_positions]
        marked = [[c[coord]] for c in marked_positions]

        regression.fit(marked, target)
        intercepts.append(regression.intercept_)
        scales.append(regression.coef_[0])

    return tuple(intercepts), tuple(scales)


#---------------------------------------------------------------------------
def save_script(dll_path, device_id, shift_factors, scale_factors):

    shift_factors = [ttrk.utils.round(x) for x in shift_factors]
    scale_factors = [ttrk.utils.round(x * 10000) / 10000 for x in scale_factors]

    commands = [
        "",
        "# Paste the following lines around the beginning of your python script",
        "import tsc2017",
        "import trajtracker as ttrk",
        "device_id = '{:}'".format(device_id),
        "dll_path = '{:}'".format(dll_path.replace("\\", "\\\\")),
        "touchpad_scale_coords_factor = {:}, {:}".format(scale_factors[0], scale_factors[1]),
        "touchpad_shift_coords_factor = {:}, {:}".format(shift_factors[0], shift_factors[1]),
        "",
        "# Paste the following lines only after calling trajtracker.initialize()",
        "touchpad = tsc2017.Touchpad(dll_path=dll_path, scale_coords_by=touchpad_scale_coords_factor, shift_coords_by=touchpad_shift_coords_factor)",
        "touchpad.connect(device_id)",
        "ttrk.env.mouse = tsc2017.Mouse(touchpad, ttrk.env.mouse)",
    ]

    script = "".join([c + "\n" for c in commands])

    print("To initialize TSC2017 in your script, please write the following python commands:\n")
    print(script)

    #-- Save script
    out_dir = os.getcwd()
    out_file = out_dir + os.sep + "dror_init_tsc.py"
    with open(out_file, 'w') as fp:
        fp.write("#\n")
        fp.write("# Paste the following commands in your script to connect with the TSC2017 device\n")
        fp.write("# Note that you may have to change device_id each time you reconnect the TSC2017 to your computer\n")
        fp.write("#\n")
        fp.write(script)

    print("\nThese commands were saved to {:}".format(out_file))


#=================================================================================================

main()
