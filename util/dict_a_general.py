"""
AmiVoice Cloudの-a-general用辞書を扱うクラス
"""
import io
import typing
import unicodedata
from . import dict_abc


class AmiVoiceDictAGeneral(dict_abc.AmiVoiceDictUtilBase):
    """接続エンジン名'-a-general'用の辞書を扱うクラス"""

    _ENGINE_NAME = "-a-general"
    _CLASS_NAMES = [
        "",
        "固有名詞",
        "名前",
        "名前(名)",
        "駅名",
        "地名",
        "会社名",
        "部署名",
        "役職名",
        "記号",
        "括弧開き",
        "括弧閉じ",
        "元号",
    ]

    @staticmethod
    def _check_yomi_chr(chr_code: int) -> bool:
        """読みの文字として禁止された文字かどうかを判定する。

        読みの文字として禁止された文字であるかを判定する。
        もし禁止された文字であれば True を返す。
        chr_codeは文字コードである(ord関数で文字コードに変換できる)。
        """
        try:
            s = chr(chr_code)
            if s == "ヴ":
                return False
            str_name = unicodedata.name(s)
            # 濁音や半濁音単体
            if "VOICED SOUND MARK" in str_name:
                return False
            # ひらがなとカタカナは定義名に含まれているはず
            if "HIRAGANA" in str_name or "KATAKANA" in str_name:
                return True
            return False
        except ValueError:
            return False

    @classmethod
    def _check_class_name(cls, class_name) -> bool:
        """指定されたクラスが正しいものか確認する"""
        return any(class_name == i for i in cls._CLASS_NAMES)

    def readdict_from_textio(self, stream: io.TextIOBase) \
            -> list[tuple[int, str]]:
        """渡されたTextIOから辞書エントリを読み込む

        streamからタブ区切りの辞書エントリを読み込む。
        辞書は1カラム目が表記、2カラム目が読み、3カラム目がクラスでなくてはならない。
        3カラム目は省略することも出来る。
        不正な形式のエントリ(行)があった場合は無視するがエラーとして記録される。
        行の先頭に'#'(シャープ)マークがあった場合は単に無視する。
        返り値は不正な値があった行番号と内容のリスト。
        エラーがなければ長さ0のリストが返る。
        """
        line_num = 0
        self._errors = []
        for tmp_line in stream:
            line = tmp_line.rstrip("\n")
            line_num += 1

            # コメントなら無視する
            if len(line) > 0 and line[0] == "#":
                continue

            # タブ分割
            splitted = line.split("\t")
            # カラム数が不正
            if len(splitted) < 2 or len(splitted) > 3:
                err_str = f"cannot split line with tab ({len(splitted)}col(s))"
                self._errors.append((line_num, err_str))
                continue

            hyouki = splitted[0].strip()
            yomi = splitted[1].strip()
            class_name = splitted[2] if len(splitted) == 3 else ""

            # 読みに不正な文字が使われていないか検査する
            is_yomi_valid = all(self._check_yomi_chr(ord(i)) for i in yomi)
            if is_yomi_valid is False:
                self._errors.append((line_num, "Invalid yomi string."))
                continue

            # クラス名が不正でないか検査する
            is_class_valid = self._check_class_name(class_name)
            if is_class_valid is False:
                self._errors.append(
                    (line_num, f"Invalid class name:{class_name}")
                )
                continue

            entry = (hyouki, yomi, class_name)
            self._entry_list.append((line_num, entry))
        return self._errors

    def get_errors(self):
        return self._errors

    def output_tsv(self):
        result_io = io.StringIO()
        for entry in self._entry_list:
            data = entry[1]
            result_io.write(f"{data[0]}\t{data[1]}\t{data[2]}\n")
        result_str = result_io.getvalue()
        return result_str
