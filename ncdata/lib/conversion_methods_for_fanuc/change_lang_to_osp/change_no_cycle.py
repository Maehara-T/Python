# coding: utf-8
from .._method import ConversionMethod

__all__ = ['ChangeNoCycle']

_FIXED_CYCLE_ENABLED = [
    'G73', 'G74', 'G76', 'G81', 'G82', 'G83', 'G84', 'G85', 'G86', 'G87', 'G88', 'G89'
]
_NO_CYCLES = [
    'L0', 'K0'
]

class ChangeNoCycle(ConversionMethod):
    def convert(self, program):
        for block in program:
            self.convert_block(block)

    def convert_block(self, block):
        adjust = 0
        copy_block = block[:]
        usedFiexedCycle = False
        for i, word in enumerate(copy_block):
            if (word[0] == 'G') and (word in _FIXED_CYCLE_ENABLED) and (not usedFiexedCycle):
                block.insert(0, 'NCYL')
                usedFiexedCycle = True
                adjust -= -1
            elif (usedFiexedCycle) and (word in _NO_CYCLES):
                del block[i + adjust]
                adjust -= 1

