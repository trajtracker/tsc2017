.. TSC2017 : Touchpad

Touchpad class
==============

Allows getting touch data from the TSC2017 device.


Using this class
----------------

1. Create a Touchpad object
2. Configure the screen size (:attr:`~tsc2017.Touchpad.output_center` and :attr:`~tsc2017.Touchpad.output_screen_size`)
3. If your TSC device reverses the coordinates horizontally or vertically, you can fix it by enabling
   :attr:`~tsc2017.Touchpad.reverse_left_right` or :attr:`~tsc2017.Touchpad.reverse_up_down`
4. :func:`~tsc2017.Touchpad.connect` to the device (provide the USB device ID you found earlier)
5. Get the touch information by calling :func:`~tsc2017.Touchpad.get_data` repeatedly.


Methods and properties
----------------------

.. autoclass:: tsc2017.Touchpad
    :members:
    :member-order: alphabetical
