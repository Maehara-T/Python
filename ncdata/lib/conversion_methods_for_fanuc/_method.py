# coding: utf-8
from abc import ABCMeta, abstractmethod

class ConversionMethod(metaclass=ABCMeta):
    """コンバーターで使用する変換方法を定義する際に、必ず継承しなければならない抽象クラス。
    このクラスを継承していない場合は、変換方法として見做されない。
    変換方法を新たに作る場合にはどのような変換方法なのかわかるよう docstring をGUIで表示させるため、
    例もつけてなるべく詳細に書くこと
    """
    @abstractmethod
    def convert(self, program):
        pass