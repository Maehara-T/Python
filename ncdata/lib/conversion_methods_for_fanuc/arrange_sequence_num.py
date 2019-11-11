# coding: utf-8
from ._method import ConversionMethod

__all__ = ['ArrangeSequenceNumber']

class ArrangeSequenceNumber(ConversionMethod):
    """メインプログラムのシーケンスナンバーを
初期値1000から増分100で整理し直す。

e.g.)

    N1100(DIA20.0 ENDMILL CHIP ARA)
    G65P4750S2000H4702E4702T11U12
    M01

    N900(DIA8.0 ENDMILL ZA ARA)
    G65P4750S800H4703F4703T12U13
    M01

    N2000(DIA11.0 ENDMILL ZA)
    G65P4750S580H4704F4704T13U14
    M01

    ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓

    N1000(DIA20.0 ENDMILL CHIP ARA)
    G65P4750S2000H4702E4702T11U12
    M01

    N1100(DIA8.0 ENDMILL ZA ARA)
    G65P4750S800H4703F4703T12U13
    M01

    N1200(DIA11.0 ENDMILL ZA)
    G65P4750S580H4704F4704T13U14
    M01
"""
    def convert(self, program, start=1000, added=100):
        for block in program:
            for i,word in enumerate(block):
                if word[0] == 'N':
                    block[i] = 'N' + str(start)
                    start += added
