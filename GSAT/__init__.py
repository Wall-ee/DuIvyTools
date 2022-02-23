"""``GMX_Simple_Analysis_Tool`` package for analysis of GMX MD results files. Written by Charles Hahn.

Python modules
----------------
The package consists of the following Python modules:
* GSAT : the CLI application.
* XPM  : module to process XPM files.
* XVG  : module to process XVG files.

"""

__version__ = "0.0.1"
from .GSAT import *
from .XPM import *
from .XVG import *

