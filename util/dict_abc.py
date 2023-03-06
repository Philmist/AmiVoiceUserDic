"""
AmiVoice Cloud用辞書ユーティリティ用の抽象クラス
"""

import io
from abc import ABC, abstractmethod


class AmiVoiceDictUtilBase(ABC):
    """辞書を扱うためのクラスの基底クラス"""

    _ENGINE_NAME: str = ""

    def __init__(self):
        # 元データの行番号と解釈された辞書
        self._entry_list: list[tuple[int, tuple[str, str, str]]] = []
        self._errors: list[tuple[int, str]] = []

    @classmethod
    def enginename(cls) -> str:
        """自身の使用が想定されるエンジン名を返す"""
        return cls._ENGINE_NAME

    @abstractmethod
    def readdict_from_textio(self, stream: io.TextIOBase) \
            -> list[tuple[int, str]]:
        """渡されたTextIOストリームから辞書データを読みこむ

        :param stream: TSVを読み込むTextIO
        :return: エラーが発見された行番号と内容のタプルのリスト
        """
        raise NotImplementedError()

    @abstractmethod
    def get_errors(self) -> list[tuple[int, str]]:
        """読み込まれたデータにエラーが発見されていた場合それを返す

        :return: エラーが発見された行番号と内容のタプルのリスト
        """
        raise NotImplementedError()

    @abstractmethod
    def output_tsv(self) -> str:
        """自身に読み込まれた辞書データをTSV(タブ区切りテキスト)形式で返す

        自身に読み込まれたデータをTSV形式の文字列で返す。
        このデータは直接AmiVoice Cloudの辞書登録で使えるものでなくてはならない。
        :return: TSV形式の辞書用文字列
        """
        raise NotImplementedError()
