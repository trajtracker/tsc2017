
import tsc2017

device_id = 'USB0::0x0451::0x2FD7::NI-VISA-40003::3::RAW'
dll_path = 'F:\\git\\tsc2017\\lib\\connect_tsc.dll'

touchpad = tsc2017.Touchpad(dll_path=dll_path, touchpad_center=(-30, 23), touchpad_size=(3696, 3634), reverse_left_right=True, output_screen_size=(1000, 100))
touchpad.connect(device_id)


print("Move your finger around the touchpad")

touching = False

while True:

    if touchpad.get_touch_data().touched != touching:
        touching = not touching
        print("Now {:}touching".format("" if touching else "not "))
