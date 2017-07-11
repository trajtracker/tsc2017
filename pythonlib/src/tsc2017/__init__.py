#------------------------------------------------------------------------------
#   TrajTracker external I/O interfaces: tsc2017 replacements
#------------------------------------------------------------------------------

def version():
    return 1, 0, 0


from ._tsc2017 import Touchpad, TouchInfo, TSCError
from ._Mouse import Mouse
