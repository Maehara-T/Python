# config utf-8
"""
NC言語を定義する際のおおもととなるクラス郡
言語を作る際は NcLanguage を継承する。
以下に注意すること
NCプログラムは必ず名前を持ち、名前をキーとしてその内容が得られるよう
NcLanguage の data フィールドに store_data メソッドを使用して格納する。
NCプログラムの内容はどのような型でも問題ないが、
String型を要求された場合に復元できるよう NcProgram を継承し、
__str__ メソッドをオーバーライドしたクラスを使用すること。
詳しくは既に作成されている .\lang\fanuc.py を参考にして下さい。
"""
from abc import ABCMeta, abstractmethod
from collections import OrderedDict

__all__ = ['NcError', 'SyntaxError', 'ParseError']

class NcError(Exception):
    pass

class SyntaxError(NcError):
    pass

class ParseError(NcError):
    def __init__(self, key, org, parsed):
        self.key = key
        self.org = org
        self.parsed = parsed

    def __str__(self):
        return """ParseError:
   {0}
-> {1}
== {2}
""".format(self.key, self.org, self.parsed)

class NcProgram(metaclass=ABCMeta):
    """解析されたNCデータを格納するクラス
    文字列を扱う事が多いため、
    String型を要求された場合に元の文字列が復元できるように __str__ メソッドをオーバーライドすること。
    """
    @abstractmethod
    def __str__(self):
        pass

class NcData(OrderedDict):
    """キーにプログラム名、値に NcProgram を継承したクラスを格納する辞書クラス"""
    def __setitem__(self, key, value):
        if isinstance(value, NcProgram):
            super().__setitem__(key, value)
        else:
            raise NcError("NcProgram を継承したクラスでは有りません。")

    def keys(self):
        return list(super().keys())

class NcLanguage(metaclass=ABCMeta):
    """NC言語の大本となるクラス
    フィールド説明
        data -> store_data でキー→プログラム名、値→ NcProgram を継承したクラスを格納する。
    """
    def __init__(self):
        self._data = NcData()

    @property
    def data(self):
        return self._data

    @abstractmethod
    def store_data(self, file_object):
        """ファイルオブジェクトを渡すことで構文解析を行い, プログラムを格納するメソッド。
        格納する際、処理しやすい型に自由に変えてよいが、必ず NcProgram を継承すること。
        data フィールドに キー→プログラム名、値→ NcProgram を継承したクラスを格納する"""
        pass

