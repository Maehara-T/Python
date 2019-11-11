# coding: utf-8
from ._method import ConversionMethod

__all__ = ['ArrangeNextToolNumber']

class ArrangeNextToolNumber(ConversionMethod):
    """メインプログラムのNextTool番号を保管する。

e.g.)

    N1000(DIA160.0 FACEMILL ARA)
    G65 P8888 S450 H6601 T9
    M01

    N1100(DIA 32.0 ENDMILL ARA)
    G65 P8888 S1500 H6618 T85 U100
    M01

    N1200(DIA12.0 ENDMILL ARA)
    G65 P8888 S1350 H6602 T55
    M01

    M30

    ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓

    N1000(DIA160.0 FACEMILL ARA)
    G65 P8888 S450 H6601 T9 U85
    M01

    N1100(DIA 32.0 ENDMILL ARA)
    G65 P8888 S1500 H6618 T85 U55
    M01

    N1200(DIA12.0 ENDMILL ARA)
    G65 P8888 S1350 H6602 T55 U9
    M01

    M30
"""
    def convert(self, program):
        tools = []
        for i, block in enumerate(program):
            hasCalled = False
            tn = None #current tool number
            tne = None #index of next tool number
            for j,word in enumerate(block):
                addr = word[0]
                if addr == 'G' and word == 'G65':
                    hasCalled = True
                elif hasCalled:
                    if addr == 'T':
                        tn = word[1:]
                    elif addr == 'U':
                        tne = j
            if hasCalled and tn:
                tools.append([i, tn, tne])
        i_b, toolnum, i_u = map(list, zip(*tools))
        toolnum = toolnum[1:] + [toolnum[0]]
        for i,t,j in zip(i_b, toolnum, i_u):
            block = program[i]
            if j:
                block[j] = 'U' + t
            else:
                block.insert(-1, 'U' + t)

