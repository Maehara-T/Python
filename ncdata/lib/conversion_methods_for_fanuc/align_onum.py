# coding: utf-8
from ._method import ConversionMethod

__all__ = ['AlignOnumber']

class AlignOnumber(ConversionMethod):
    """4桁未満のO番号と、
G65, G66, M98を含むブロックのPから始まる4桁未満のワードに対して、
4桁のO番号となるよう先頭に0を追加する。

e.g.)

    O10
    M98 P200
    M99

    O200
    M99

    O2000
    M99

    ↓↓↓↓↓

    O0010
    M98 P0200
    M99

    O0200
    M99

    O2000
    M99
"""
    def convert(self, program):
        for block in program:
            self.convert_block(block)

    def convert_block(self, block):
        hasCall = [True for code in ['G65', 'G66', 'M98'] if code in block]
        for i, word in enumerate(block):
            if (word[0] == 'O') or (hasCall and word[0] == 'P' and "#" not in word):
                add = '0' * ((len(word) - 5) * (-1))
                block[i] = add.join([word[:1], word[1:]])
