##############################################################################################################
#
# Utility for testing and calibrating the TSC2017: see that it works well, and adapt its coordinate space
# with TrajTracker's
#
##############################################################################################################

import os
import time
import numpy as np
import msvcrt

import expyriment as xpy
import trajtracker as ttrk
import trajtracker.utils as u

from tsc2017 import Touchpad, TSCError
import setup_utils as sut


#============================================================================
#   To configure what this utility does
#============================================================================

#-- To simulate this app with mouse rather than with the real touchpad
simulate_with_mouse = False

test_directions = True
test_bounds = True

#===============================================================================================

axis_adverb = ['horizontally', 'vertically']
direction_per_axis = [['left', 'right'], ['down', 'up']]
side_per_axis = [['left', 'right'], ['bottom', 'top']]


#---------------------------------------------------------------------------
def main():

    print("")
    print("-------------------------------------------------")
    print("     Establishing connection with TSC2017")
    print("-------------------------------------------------")
    print("")

    device_id = "N/A"
    dll_path = "N/A"

    if simulate_with_mouse:
        xpy.control.defaults.window_mode = True
        ttrk.log_to_console = True

        exp = ttrk.initialize()
        xpy.control.start(exp)
        exp.mouse.show_cursor()
        touchpad = sut.TouchpadMouseSimulator(exp, ttrk.env.mouse)

    else:
        dll_path = get_dll_path()
        dll_path += "\\connect_tsc.dll"
        touchpad = Touchpad(dll_path)
        device_id = connect_to_device(touchpad)

    reverse_vertical = False
    reverse_horizontal = False

    if test_directions:

        print("")
        print("-------------------------------------------------")
        print("     Testing movement directions")
        print("-------------------------------------------------")

        while True:

            print("\nPlease move your finger UPWARDS on the touchpad slowly, several times")
            is_up_positive = get_movement_direction_along_axis(1, touchpad, min_movements=3)

            print("\nPlease move your finger DOWNWARDS on the touchpad slowly, several times")
            is_down_positive = get_movement_direction_along_axis(1, touchpad, min_movements=3)

            if is_up_positive == is_down_positive:
                print("\nProblem: it seems that you moved your finger in the same direction both when I asked you to move upwards and downwards. Try again.")
            else:
                reverse_vertical = is_down_positive
                print("\n>>> Conclusion: TSC2017's positive coordinates are on the {:}".format("top" if is_up_positive else "bottom"))
                break

        while True:

            print("\nPlease move your finger LEFTWARDS on the touchpad slowly, several times")
            is_left_positive = get_movement_direction_along_axis(0, touchpad, min_movements=3)

            print("\nPlease move your finger RIGHTWARDS on the touchpad slowly, several times")
            is_right_positive = get_movement_direction_along_axis(0, touchpad, min_movements=3)

            if is_left_positive == is_right_positive:
                print("\nProblem: it seems that you moved your finger in the same direction both when I asked you to move left and right. Try again.")
            else:
                reverse_horizontal = is_left_positive
                print("\n>>> Conclusion: TSC2017's positive coordinates are on the {:}".format("left" if is_left_positive else "right"))
                break

    print("")
    print("-------------------------------------------------")
    print("     Detecting touchpad boundaries")
    print("-------------------------------------------------")
    print("")

    if test_bounds:
        top_bound = detect_bounds(touchpad, 1, True, reverse_vertical)
        bottom_bound = detect_bounds(touchpad, 1, False, reverse_vertical)
        left_bound = detect_bounds(touchpad, 0, False, reverse_horizontal)
        right_bound = detect_bounds(touchpad, 0, True, reverse_horizontal)
        print("\n>>> Touchpad boundaries: top={:}, bottom={:}, left={:}, right={:}".format(top_bound, bottom_bound, left_bound, right_bound))

    else:
        top_bound = 0
        bottom_bound = 0
        left_bound = 0
        right_bound = 0

    print("-------------------------------------------------")
    print("     Visual test")
    print("-------------------------------------------------")

    print("Now, move your finger around the touchpad. A dot should appear on screen in the corresponding location.")
    print("Check that the dot is moving in accordance with your finger. Press <SPACE> when you're finished")

    print("Did the dot move according to your finger movement?")

    print("-------------------------------------------------")
    print("     Calibration finished")
    print("-------------------------------------------------")

    save_script(dll_path, device_id, reverse_horizontal, reverse_vertical,
                top_bound, bottom_bound, left_bound, right_bound)

    if simulate_with_mouse:
        xpy.control.end()


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


#---------------------------------------------------------------------------
# Get movement data and:
# 1. Make sure that the main movement is along the specified axis and not the other axis
# 2. Check the movement direction along that axis (positive or negative)
def get_movement_direction_along_axis(axis, touchpad, min_movement_duration=0.5, min_movements=1):

    n_negative = 0
    n_positive = 0

    dir_name = {True: '+', False: '-'}

    while True:
        is_positive, xy = get_one_movement_along_axis(axis, touchpad, min_movement_duration)
        print("Detected a movement in direction {:}".format(dir_name[is_positive]))
        n_positive += int(is_positive)
        n_negative += int(not is_positive)
        # noinspection PyUnresolvedReferences
        if np.abs(n_positive - n_negative) >= min_movements:
            break

    return n_positive > n_negative


#---------------------------------------------------------------------------
# Get movement data and:
# 1. Make sure that the main movement is along the specified axis and not the other axis
# 2. Check the movement direction along that axis (positive or negative)
# noinspection PyTypeChecker
def get_one_movement_along_axis(axis, touchpad, min_movement_duration=0.5):

    other_axis = 1 - axis

    while True:

        movement_time, x, y = get_movement(touchpad)
        xy = x, y

        if movement_time < min_movement_duration:
            print("The movement was too short ({:.1f} seconds, expecting at least {:.1f}), try again".format(movement_time, min_movement_duration))
            continue

        std_xy = np.std(x), np.std(y)
        if std_xy[other_axis] > std_xy[axis]:
            print("You moved {:} instead of {:}; try again".format(axis_adverb[other_axis], axis_adverb[axis]))
            continue

        if std_xy[other_axis] > std_xy[axis] / 2:
            print("You should have moved {:} but you also moved {:}. Try again".format(axis_adverb[axis], axis_adverb[other_axis]))
            continue

        d = np.diff(xy[axis])
        n_pos = sum(d > 0)
        n_neg = sum(d < 0)

        if n_pos > 2 * n_neg:
            return True, xy[axis]

        if n_neg > 2 * n_pos:
            return False, xy[axis]

        print "I am not sure if you moved {:} or {:}, please try again".format(direction_per_axis[axis][0], direction_per_axis[axis][1])


#---------------------------------------------------------------------------
def detect_bounds(touchpad, axis, positive, axis_reversed, min_movement_duration=0.3):

    direction_ind = (1-positive) if axis_reversed else int(positive)
    side_name = side_per_axis[axis][direction_ind]

    print("")
    print("")
    print("Detecting the touchpad's {:} border".format(side_name.upper()))
    print("")

    bounds = [
        detect_movement_towards_bound(touchpad, axis, positive, axis_reversed, 0, min_movement_duration),
        detect_movement_towards_bound(touchpad, axis, positive, axis_reversed, 0, min_movement_duration),
        detect_movement_towards_bound(touchpad, axis, positive, axis_reversed, 2, min_movement_duration),
        detect_movement_towards_bound(touchpad, axis, positive, axis_reversed, 2, min_movement_duration),
        detect_movement_towards_bound(touchpad, axis, positive, axis_reversed, 1, min_movement_duration),
        detect_movement_towards_bound(touchpad, axis, positive, axis_reversed, 1, min_movement_duration),
    ]

    print("End-of-touchpad boundary: {:}".format(bounds))
    if max(bounds) - min(bounds) > 100:
        print ">>> PROBLEM: The bounds information is inconclusive - large variance"

    return int(np.average(bounds))


#---------------------------------------------------------------------------
def detect_movement_towards_bound(touchpad, axis, expect_positive, axis_reversed, move_on, min_movement_duration):
    """

    :param touchpad:
    :param axis: 0 or 1
    :param expect_positive: Whether the finger should move in the positive direction (up or right)
    :param axis_reversed: Whether the touchpad reverses this axis info
    :param move_on: On which screen location to move: 0=left/bottom, 1=right/top, 2=middle
    :param min_movement_duration: in seconds
    :return: The bound (int)
    """

    direction_ind = (1 - expect_positive) if axis_reversed else int(expect_positive)
    bound_direction_name = direction_per_axis[axis][direction_ind]
    orthogonal_direction = side_per_axis[1-axis][move_on] if move_on in (0, 1) else "middle"

    while True:

        print("\nPlease place your finger on the {:} of the touchpad and move it {:} until it exits the touchpad".
              format(orthogonal_direction, bound_direction_name))
        print("   DO NOT LIFT YOUR FINGER BEFORE IT LEAVES THE TOUCHPAD")

        #-- Get the movement
        is_positive, x_or_y = get_one_movement_along_axis(axis, touchpad, min_movement_duration)
        if is_positive != expect_positive:
            print("You moved {:}wards instead of {:}wards. Please try again.".
                  format(direction_per_axis[axis][1 - direction_ind], direction_per_axis[axis][direction_ind]))
            continue

        #-- Get the most extreme coordiante
        bound = max(x_or_y) if expect_positive else min(x_or_y)

        print("Good! bound = {:}".format(bound))

        return bound


#---------------------------------------------------------------------------
# Get movement data and:
# 1. Make sure that the main movement is along the specified axis and not the other axis
# 2. Check the movement direction along that axis (positive or negative)
def get_movement(touchpad):

    raw_input("Hit <ENTER> before you start moving")
    print("OK, go now")

    #-- Wait until touchpad is touched
    while not touchpad.get_touch_data().touched:
        time.sleep(0.01)

    start_time = u.get_time()

    x = []
    y = []

    #-- Get movement data
    while True:
        td = touchpad.get_touch_data()
        if not td.touched:
            break

        x.append(td.x)
        y.append(td.y)

    movement_time = u.get_time() - start_time

    return movement_time, x, y


#---------------------------------------------------------------------------
def save_script(dll_path, device_id, reverse_horizontal, reverse_vertical,
                top_bound, bottom_bound, left_bound, right_bound):

    mid_x = int((left_bound + right_bound) / 2)
    mid_y = int((top_bound + bottom_bound) / 2)
    # noinspection PyUnresolvedReferences
    width = np.abs(left_bound - right_bound)
    # noinspection PyUnresolvedReferences
    height = np.abs(top_bound - bottom_bound)

    args = "output_center=({:}, {:}), output_screen_size=({:}, {:})".format(mid_x, mid_y, width, height)

    if reverse_horizontal:
        args += ", reverse_left_right=True"

    if reverse_vertical:
        args += ", reverse_up_down=True"

    commands = [
        "device_id = '{:}'".format(device_id),
        "dll_path = '{:}'".format(dll_path),
        "touchpad = tsc2017.Touchpad(dll_path{:})".format(args),
        "touchpad.connect(device_id)",
    ]

    script = "".join([c + "\n" for c in commands])

    print("To initialize TSC2017 in your script, please write the following python commands:\n")
    print(script)

    #-- Save script
    out_dir = os.getcwd()
    out_file = out_dir + os.sep + "init_tsc_command.py"
    with open(out_file, 'w') as fp:
        fp.write("#\n")
        fp.write("# Paste the following commands in your script to connect with the TSC2017 device\n")
        fp.write("# Note that you may have to change device_id each time you reconnect the TSC2017 to your computer\n")
        fp.write("#\n")
        fp.write(script)

    print("\nThese commands were saved to {:}".format(out_file))


#=================================================================================================

main()
