# coding: utf-8
from decimal import *
from ._method import ConversionMethod

__all__ = ['Multiplication']

def is_integer(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return float(n).is_integer()

class Multiplication(ConversionMethod):
    """指定したアドレスに指定した値を掛ける。
コンソール画面で、対象となるアドレスと掛ける値を入力しなければならない。
"""
    def __init__(self, addr='', num=''):
        self.addr = addr
        self.num  = num

    def convert(self, program):
        self.init_field()
        for block in program:
            self.convert_block(block)

    def convert_block(self, block):
        for i, word in enumerate(block):
            addr = word[0]
            if addr in self.addr:
                try:
                    block[i] = addr + str(self.calc(word[1:]))
                except:
                    pass

    def calc(self, num:str):
        return (
            Decimal(num) * Decimal(self.num) if '.' in num else
            int(num) * int(self.num) if not '.' in self.num else
            Decimal(int(num) * Decimal(self.num)).quantize(0, rounding=ROUND_HALF_EVEN)
        )

    def init_field(self):
        while True:
            if self.addr.isalpha():
                break
            self.addr = input('対象となるアドレスを羅列して下さい。 -> ').upper()
        while True:
            if is_integer(self.num):
                break
            self.num = input('掛ける値を入力して下さい。 -> ')

