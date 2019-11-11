# coding: utf-8
from .._method import ConversionMethod
import re

__all__ = ['ChangeVariables']

_LOCAL_VAL = {
        '#1' : "A",
        '#2' : "B",
        '#3' : "C",
        '#4' : "I",
        '#5' : "J",
        '#6' : "K",
        '#7' : "D",
        '#8' : "E",
        '#9' : "F",
        '#11': "H",
        '#13': "M",
        '#17': "Q",
        '#18': "R",
        '#19': "S",
        '#20': "T",
        '#21': "U",
        '#22': "V",
        '#23': "W",
        '#24': "X",
        '#25': "Y",
        '#26': "Z",
}
_SUB_PATTERN = re.compile(r'({})(?=$|[^0-9])'.format('|'.join(sorted(_LOCAL_VAL.keys(), reverse=True))))

def get_changed_word(word):
    word = _SUB_PATTERN.sub(lambda m: _LOCAL_VAL[m.group(1)]*2, word)
    if (word[0].isalpha()) and ('=' not in word):
        word = word[0] + '=' + word[1:]
    word = word.replace('#0', 'EMPTY')
    word = word.replace('#', 'V')
    return word

class ChangeVariables(ConversionMethod):
    """G65, G66の引数と変数を以下のように変換する。

e.g.)

    G65 X100.0 Y#20
    IF [#1 EQ #0] GOTO1
    #101 = #1 + 10.0

    ↓↓↓↓↓↓↓↓↓↓↓

    G65 XX=100.0 YY=TT
    IF [AA EQ EMPTY] GOTO1
    V101 = AA + 10.0
"""
    def convert(self, program):
        for block in program:
            self.convert_block(block)

    def convert_block(self, block):
        if 'G65' in block or 'G66' in block:
            hasCall = True
        else:
            hasCall = False
        for i in range(len(block)):
            if hasCall and block[i][0].isalpha() and block[i][0] not in ['G', 'P']:
                block[i] = block[i][0]*2 + '=' + block[i][1:]
            if '#' in block[i]:
                block[i] = get_changed_word(block[i])
