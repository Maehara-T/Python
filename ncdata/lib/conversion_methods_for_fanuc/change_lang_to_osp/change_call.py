# coding: utf-8

from .._method import ConversionMethod

__all__ = ['ChangeCall']

class ChangeCall(ConversionMethod):
    """CALL, MODINが含まれているブロックの Pから始まるワードを
プログラムの呼び出しと見なして PXXXX から OXXXX に変換する。
"""
    def convert(self, nc_program):
        for block in nc_program:
            self.convert_block(block)

    def convert_block(self, block):
        if 'CALL' in block or 'MODIN' in block:
            for i, word in enumerate(block):
                if word[0] == 'P':
                    block[i] = 'O' + word[1:]

