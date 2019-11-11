# coding: utf-8
from .._method import ConversionMethod

__all__ = ['SimpleReplace']

_DICT = {
    'M99': 'RTS',
    'G84': 'G284',
    'G65': 'CALL',
    'G66': 'MODIN',
    'G67': 'MODOUT',
    'M98': 'CALL',
}

class SimpleReplace(ConversionMethod):
    """_DICTに従って単純置換を行う。"""
    def convert(self, program):
        for block in program:
            self.convert_block(block)

    def convert_block(self, block):
        for i, word in enumerate(block):
            if word in _DICT.keys():
                block[i] = _DICT[word]

