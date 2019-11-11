
import os
import sys
import pathlib
_temp = os.getcwd()
os.chdir(str(pathlib.Path(__file__).parent))
sys.dont_write_bytecode = True

from .nc import *
from . import langs

os.chdir(_temp)
