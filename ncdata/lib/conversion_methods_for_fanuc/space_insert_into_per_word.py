# coding: utf-8
from ._method import ConversionMethod

__all__ = ['SpaceInsertIntoPerWord']

class SpaceInsertIntoPerWord(ConversionMethod):
    """ワード間にスペースが含まれていない場合、
スペースを追加してデータの可読性を上げる。

e.g.)

    G01X100Y200
    G65 X100 Y200Z100

    ↓↓↓↓↓↓↓↓↓

    G01 X100 Y200
    G65 X100 Y200 Z100
"""
    def convert(self, program):
        for block in program:
            self.convert_block(block)

    def convert_block(self, block):
        count = 0
        copy = block[:]
        previous = ' '
        for i, word in enumerate(copy):
            if (word != ' ') and (previous != ' ') and (word != '\n'):
                block.insert(i + count, ' ')
                count += 1
            previous = word
