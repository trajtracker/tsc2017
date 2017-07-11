.. TSC2017 : Touchpad

Touchpad class
==============

Allows getting touch data from the TSC2017 device.


Using this class
----------------

1. Create a Touchpad object

2. Configure how the touchpad's coordinates should be rescaled so that they match the screen coordinates
   (:attr:`~tsc2017.Touchpad.scale_coords_by` and :attr:`~tsc2017.Touchpad.shift_coords_by`).

   See :doc:`here <how_to_configure>` how you can get these scaling factors.

3. :func:`~tsc2017.Touchpad.connect` to the device (provide the USB device ID you found earlier)

4. Get the touch information by calling :func:`~tsc2017.Touchpad.get_touch_data` repeatedly.


Methods and properties
----------------------

.. autoclass:: tsc2017.Touchpad
    :members:
    :member-order: alphabetical
