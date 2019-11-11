# -*- coding: utf-8 -*-
from decimal                 import Decimal
from ...                     import gcodes
from ...generic              import insert_space
from ...generic.align_digits import AlignToFloat

class ChangeFiexdCycle:
    def __init__(self, point_init='100.0'):
        self.point_init = Decimal(point_init)
        self.fixedcycle = [v[1:] for v in gcodes.FIXED_CYCLE_ENABLED]

    def exec_per_program(self, program):
        elms = GetElements(program)
        for e in elms:
            fdict            = self._get_fixedcycle_dict(e)
            program[e[0][0]] = self._get_new_block(fdict)
            del program[e[1][0]]
        return program

    def _get_fixedcycle_dict(self, elm):
        fdict = {}
        for word in elm[0][1]:
            addr = 'Q' if word[0] == 'P' else word[0]
            val  = word if addr == '(' else word[1:]
            if fdict.get(addr): fdict[addr].append(val)
            else              : fdict[addr] = [val]
        for word in elm[1][1]:
            addr = word[0]
            val  = word if addr == '(' else word[1:]
            if fdict.get(addr): fdict[addr].append(val)
            else              : fdict[addr] = [val]
        fdict['Z'] = self._get_new_deeps(fdict['Z'])
        fdict['R'] = self._get_new_refs(fdict['R'])
        fdict['G'] = [v for v in fdict['G'] if v in self.fixedcycle]
        fdict['P'] = [v + '.' for v in fdict['P']]
        if fdict.get('Q'):
            fdict['Q'] = [str(AlignToFloat().align(v)) for v in fdict['Q']]
        return fdict

    def _get_new_deeps(self, deeps):
        return [
            str((AlignToFloat().align(deep) + Decimal('2.0')) * (-1))
                for deep in deeps
        ]

    def _get_new_refs(self, refs):
        new_refs = list()
        for ref in refs:
            ref  = AlignToFloat().align(ref)
            calc = ref + self.point_init - Decimal('2.0')
            new_refs.append(
                '#113'                     if calc == 0 else
                '[#113+' + str(calc) + ']' if calc  > 0 else
                '[#113'  + str(calc) + ']'
            )
        return new_refs

    def _get_new_block(self, fdict):
        new_block = (
            ['G65', 'P8100'] +
            ['M' + v for v in fdict['G']] +
            ['I' + v for v in fdict['P']] +
            ['Z' + v for v in fdict['R']] +
            ['R2.0'] +
            ['W' + v for v in fdict['Z']] +
            ['F' + v for v in fdict['F']]
        )
        if fdict.get('('):
            new_block += ['('+v for v in fdict['(']]
        new_block += (
            ['Q'+v for v in fdict['Q']] if fdict.get('Q') else
            ['S#19']                    if fdict['G'][-1] == '84' else
            ['']
        )
        return insert_space.exec_per_block(new_block + ['\n'])

#*********************************************************************************

class GetElements:
    def __init__(self, program):
        self.program = iter(program[:])
        self.index   = -1

    def __iter__(self):
        elms = []
        for block in self.program:
            self.index += 1
            if self._usedFixedcycle(block):
                elms.append([self.index, block])
            elif ( elms ) and ( 'M98' in block ):
                elms.append([self.index, block])
                yield elms
                elms        = []
                self.index -= 1

    def _usedFixedcycle(self, block):
        for c in gcodes.FIXED_CYCLE_ENABLED:
            if c in block:
                return True

