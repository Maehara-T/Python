# coding: utf-8
from .align_digits import *
from ._method import ConversionMethod

__all__ = ['ChangeToAbs', 'ChangeToInc']
_IGNORE_CODE = [
    'G65', 'G66'
    'G73', 'G74', 'G76', 'G81', 'G82', 'G83', 'G84', 'G85', 'G86', 'G87', 'G88', 'G89'
    'G04', 'G4',
    'M98'
]

class ChangeCoordinateSystem(ConversionMethod):
    def __init__(self, default=None, numtype=None, addr=['X', 'Y', 'Z']):
        self.default = default
        self.numtype = numtype
        self.addr = addr
        self.ignore = _IGNORE_CODE

    def convert(self, program):
        self.init_field()
        self.set_coord_gcode(self.default)
        self.values = [0, 0, 0]
        for block in program:
            self.convert_block(block)

    def convert_block(self, block):
        self.prev_values = self.values[:]
        for i, word in enumerate(block):
            addr = word[0]
            if (addr == 'G' or addr == 'M') and word in self.ignore:
                continue
            elif addr in self.addr:
                try:
                    num = self.aligntype.calc(word[1:])
                    index = ord(addr) - 88 # X->0, Y->1, Z->2
                    result = self.calc_method(index, num)
                    block[i] = addr + (result if self.shouldChange else str(num))
                except:
                    pass
            elif addr == 'G' and word in ['G90', 'G91']:
                block[i] = self.output
                self.set_coord_gcode(word)

    def init_field(self):
        while True:
            if self.default in ['G90', 'G91']:
                break
            self.default = input('G90, G91が不明な場合、どのように振る舞うか (G90 or G91) -> ').upper()
        while True:
            if self.numtype in ['I', 'F']:
                break
            self.numtype = input('数値データの型をどのように揃えるか (float -> F or int -> I) -> ').upper()
        self.aligntype = AlignToInt() if self.numtype == 'I' else AlignToFloat()

    def set_coord_gcode(self, gcode):
        self.shouldChange = False if gcode == self.output else True
        self.calc_method = getattr(self, '_calc_method_' + gcode)

    def _calc_method_G90(self, index, value):
        new_value = value - self.prev_values[index]
        self.values[index] = value
        return str(new_value)

    def _calc_method_G91(self, index, value):
        new_value = value + self.prev_values[index]
        self.values[index] = new_value
        return str(new_value)


class ChangeToAbs(ChangeCoordinateSystem):
    """XYZの数値データを絶対値に変換すると同時に、
XYZの数値データの型(Float or Int)を揃える。
'G65', 'G66', 'M98', 'G04', 及び 固定サイクルが含まれるブロックは変換しない。


変換を行う前に、コンソール画面で以下の設定が必要

    ・G90, G91が不明な場合、どのように振る舞うか (G90 or G91)

    ・Float型(小数点を含まない場合は1/1000倍し小数点を追加),
      Int型(小数点を含んでいる場合は1000倍して小数点を削除)
      どちらで揃えるのか (f or i)
        Float型 -> f
        Int型 -> i
"""
    output = 'G90'

class ChangeToInc(ChangeCoordinateSystem):
    """XYZの数値データを相対値に変換すると同時に、
XYZの数値データの型(Float or Int)を揃える。
'G65', 'G66', 'M98', 'G04', 及び 固定サイクルが含まれるブロックは変換しない。


変換を行う前に、コンソール画面で以下の設定が必要

    ・G90, G91が不明な場合、どのように振る舞うか (G90 or G91)

    ・Float型(小数点を含まない場合は1/1000倍し小数点を追加),
      Int型(小数点を含んでいる場合は1000倍して小数点を削除)
      どちらで揃えるのか (f or i)
        Float型 -> f
        Int型 -> i
"""
    output = 'G91'

