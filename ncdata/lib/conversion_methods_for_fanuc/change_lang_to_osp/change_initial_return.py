# coding: utf-8
from .._method import ConversionMethod

__all__ = ['ChangeInitialReturn']

class ChangeInitialReturn(ConversionMethod):
    def __init__(self, point_initial='100.0'):
        self.point_initial = point_initial

    def convert(self, program):
        for i, block in enumerate(program):
            for word in block:
                if word == 'G98':
                    program[i].remove('G98')
                    program[i].insert(-1, 'M53')
                    program.insert(i, ['G71', 'Z{0}'.format(self.point_initial), '\n'])

