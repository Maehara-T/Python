# coding: utf-8
from .._method import ConversionMethod
from ..align_digits import *

__all__ = ['AlignArgs']

FIXED_CYCLE_ENABLED = [
    'G73', 'G74', 'G76', 'G81', 'G82', 'G83', 'G84', 'G85', 'G86', 'G87', 'G88', 'G89'
]
ALIGN = [
    [FIXED_CYCLE_ENABLED, AlignToFloat(addr='PQ')]
]

class AlignArgs(ConversionMethod):
    """固定サイクルのP, Qの値を
Float型(小数点が含まれていなければ1/1000倍)に変換する。"""
    def convert(self, program):
        for block in program:
            for i in ALIGN:
                for j in i[0]:
                    if j in block:
                        i[1].convert_block(block)
                        break

