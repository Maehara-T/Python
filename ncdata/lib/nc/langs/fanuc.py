# config utf-8
"""
<Filename HOGE.NC>
================================================
(AAA)

O100
X#24 Y100 Z100
#10 = #100 +100
X[[#10 + 20] +SIN[1]]Y100
Z***
M99

O200
X200,Y100

================================================

上記のような'HOGE.NC'というNCデータが有る場合
Fanuc クラスの store_data メソッドにファイルオブジェクトを渡すことで
定義された正規表現のパターンに従い、以下のように data フィールドにプログラム内容が格納される。

================================================
fnc = Fanuc()
with open('HOGE.NC', 'r') as f
    fnc.store_data(f)

fnc.data = {
    'BEGIN': FanucProgram(
        [
            ["(AAA)", "\n"],
            ["\n"],
        ]
    ),
    'O100': FanucProgram(
        [
            ["X#24", " ", "Y100", " ", "Z100", "\n"],
            ["#10", " ", "= #100 +100", "\n"],
            ["X[[#10 + 20] +SIN[1]]", "Y100", "\n"],
            ["Z***", "\n"],
            ["M99", "\n"],
            ["\n"],
        ]
    'O200': FanucProgram(
        [
            ["X200", "Y100", "\n"],
            ['\n'],
        ]
    )
}
================================================

最初に定義されている O100 以前の部分は
内容が欠落しないよう仮のプログラム名'BEGIN'として保存される。
NCプログラムとして不正な文字やおかしな表現が使用されている場合には(例 O200 内の ",")
ParseError を throw してコンソール画面にその箇所を表示する。
また

str(fnc.data('O100'))

で元の文字列である

O100
X#24 Y100 Z100
#10 = #100 +100
X[[#10 + 20] +SIN[1]]Y100
Z***
M99

が取得できるよう nc.NcProgram を継承した FanucProgram を定義し、このクラスを入れ物としている。
新たな言語が必要になったときは参考にして下さい。
"""
import re
import regex
from .. import nc

__all__ = ['parse_block', 'Fanuc']

# パターンマッチングさせる表現
SPECIALLY_ALLOWED_WORD = r"\*\*\*"
COMMENT = r"\( [^\(]*? \)"
BLOCK_SKIP = r"/d?"
STATEMENT = r"(?:IF) | (?:THEN) | (?:WHILE) | (?:DO) | (?:END) | (?:GOTO\d+)"
ADDRESS = r"[A-Z] -? [ ]?"
NUMBER = r"(?:\d+\.?\d*) | (?:\d*\.?\d+)"
VARIABLE = r"\#\d+"
ASSIGN = r"=[^\n]*"
OPERATOR = r" \+ | - | \* | / | (?:MOD) | (?:AND) | (?:OR) | (?:XOR)"
COMPARISON = r"(?:EQ) | (?:NE) | (?:LT) | (?:LE) | (?:GT) | (?:GE)"
FUNC_PREFIX = r"""
    (?:SIN) | (?:COS) | (?:TAN) | (?:ASIN) | (?:ACOS) | (?:ATAN) | (?:ROUND) | (?:FIX) | (?:FUP) |
    (?:SQRT) | (?:ABS) | (?:BIN) | (?:BCD) | (?:EXP) | (?:POW) | (?:ADP)
"""

WORD = r"{ADDRESS} (?: (?:{NUMBER}) | (?:{VARIABLE}) | (?:{SPECIALLY_ALLOWED_WORD}))".format(**globals())
CALC_TOKEN = r"""(?:
    \s |
    (?:{COMMENT}) |
    (?:{NUMBER}) |
    (?:{VARIABLE}) |
    (?:{OPERATOR}) |
    (?:{COMPARISON})
)""".format(**globals())

CALC = r"""(?<calc>
    (?: (?: \# | (?:{FUNC_PREFIX}) )?
        \[ (?:
            (?: {CALC_TOKEN}) |
            (?&calc)
        )+ \]
    )+ )
""".format(**globals())

BRACKET_NOT_IN_BLOCK = re.compile(r"""(?:
    \s |
    (?:{COMMENT}) |
    (?:{BLOCK_SKIP}) |
    (?:{STATEMENT}) |
    (?:{ASSIGN}) |
    (?:{VARIABLE}) |
    (?:{WORD})
)""".format(**globals()), re.X)

BRACKET_IN_BLOCK = regex.compile(r"""(?:
    \s |
    (?:{COMMENT}) |
    (?:{BLOCK_SKIP}) |
    (?:{STATEMENT}) |
    (?:{ASSIGN})|
    (?: (?:{ADDRESS})? (?:{CALC}) ) |
    (?:{VARIABLE}) |
    (?:{WORD})
)""".format(**globals()), re.X)


def parse_block(block:str):
    """ブロックを解析し、トークンのリストを得る
    トークンを復元して、元の文字列が得られなかった場合は、
    不正な表現があると判別して、ParseError を throw する。
    """
    # すべてのブロックで括弧の入れ子を検出させようとすると動作が遅くなるため
    # '[' が ブロックに含まれている場合のみ 入れ子を検出させる
    if '[' not in block:
        token = BRACKET_NOT_IN_BLOCK.findall(block)
    else:
        token = [i.group() for i in BRACKET_IN_BLOCK.finditer(block)]
    if block != ''.join(token):
        raise nc.ParseError('', block, token)
    else:
        return token

class FanucProgram(list, nc.NcProgram):
    def __str__(self):
        return ''.join([''.join(block) for block in self])

class Fanuc(nc.NcLanguage):
    def store_data(self, file_object):
        key = 'BEGIN'
        self.data[key] = FanucProgram([])
        for block in file_object:
            try:
                token = parse_block(block)
            except nc.ParseError as e:
                e.key = key
                token = e.parsed
                print(e)
            finally:
                if 'O' in block:
                    define = [word for word in token if word[0]=='O']
                    if len(define) is not 0:
                        key = define[-1]
                        self.data[key] = FanucProgram([])
                self.data[key].append(token)

