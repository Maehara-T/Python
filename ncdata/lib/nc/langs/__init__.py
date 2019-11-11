
import os
import pathlib
_temp = os.getcwd()
os.chdir(str(pathlib.Path(__file__).parent))


from .fanuc import *


os.chdir(_temp)
