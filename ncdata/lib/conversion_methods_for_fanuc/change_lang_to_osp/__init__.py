
import pathlib
import os
_temp = os.getcwd()
os.chdir(str(pathlib.Path(__file__).parent))

from .._method import ConversionMethod
from ..align_digits import *
from ..space_insert_into_per_word import *
from ..align_onum import *
from .change_variables import *
from .simple_replace import *
from .change_initial_return import *
from .change_no_cycle import *
from .align_args import *
from .change_call import *

__all__ = ['ChangeLangToOSP']
_METHODS = [
    AlignToFloat(),
    AlignOnumber(),
    AlignArgs(),
    ChangeInitialReturn(),
    ChangeVariables(),
    ChangeNoCycle(),
    SimpleReplace(),
    ChangeCall(),
    SpaceInsertIntoPerWord(),
]
_DOCS = ''
for m in _METHODS:
    _DOCS += '<{0}>:\n {1}\n\n'.format(m.__class__.__name__, m.__doc__)

class ChangeLangToOSP(ConversionMethod):
    def convert(self, program):
        for m in _METHODS:
            m.convert(program)

ChangeLangToOSP.__doc__ = "以下に記すメソッドを順番に使用してOSPのデータに変換する。\n\n{0}".format(_DOCS)

os.chdir(_temp)

