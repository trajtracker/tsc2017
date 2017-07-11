.. TSC2017: how-to-configure

How to configure the TSC2017
============================

The TSC2017 detects the touch position in 4096 x 4096 resolution.

However, there are several issues with its output coordinates:

- The application that uses the touch information usually expects to get it in the screen's coordinate
  space, which is different.

- The touchpad sometimes has slightly lower resolution (so instead of returning coordinates in the range
  0-4095 it would sometimes ignore ~200 pixels to each direction, i.e., the physical device would
  correspond with coordinates ~200 to ~3900).

- Some devices flip the coordinates horizontally or vertically (perhaps due to incorrect hardware configuration,
  we're not sure why)

- When you place the touchpad on top of a screen, there device may be slightly shifted relatively to the screen.


To solve all these issues, use the setup_tsc.py calibration script. It shows several dots and asks you to touch
each of them. Then, the script calculates how the TSC2017 output should be shifted and rescaled to align it
with the screen's coordinate space.

The output of this script is a small file called *results_to_paste_in_your_script.py*, containing lines of code
that you should paste in your experiment main script.
