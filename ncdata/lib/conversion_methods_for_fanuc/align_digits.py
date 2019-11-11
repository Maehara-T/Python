# coding: utf-8
from decimal import Decimal
from .multiplication import *

__all__ = ['AlignToInt', 'AlignToFloat']

class AlignToInt(Multiplication):
    """XYZIJKの数値データの型を
Int型(小数点を含んでいる場合は1000倍して小数点を削除)に揃える。

e.g.)

    G01 X0.1 Y0.2 Z0.1
    G03 X1.0 Y0.2 R1.0

    ↓↓↓↓↓↓↓↓↓

    G01 X100 Y200 Z100
    G03 X100 Y200 R1.0

"""
    def __init__(self, addr='XYZIJK', num=1000):
        super().__init__(addr=addr, num=num)

    def calc(self, num):
        return (
            int(Decimal(num) * self.num) if '.' in num else
            int(num)
        )

class AlignToFloat(Multiplication):
    """XYZIJKの数値データの型を
Float型(小数点を含まない場合は1/1000倍し小数点を追加)に揃える。

e.g.)

    G01 X100 Y200 Z100
    G03 X1.0 Y200 R1.0

    ↓↓↓↓↓↓↓↓↓

    G01 X0.1 Y0.2 Z0.1
    G03 X1.0 Y0.2 R1.0
"""
    def __init__(self, addr='XYZIJK', num=1000):
        super().__init__(addr=addr, num=num)

    def calc(self, num):
        return (
            Decimal(num) if '.' in num else
            Decimal(num + '.0') / self.num
        )

