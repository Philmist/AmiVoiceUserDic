# AmiVoiceで使う自分用辞書(とスクリプト)セット

このリポジトリはPhilmistが配信で使っている
AmiVoice Cloud用のユーザー辞書と管理のためのスクリプトをセットにしたものです。

自分だけが使うのを想定しているので作りが雑です。ご了承ください。

## スクリプト

AmiVoice Cloudはマイページから1000個までの単語を登録できるのですが、
配信によって単語の登録を切り替えるとなるとけっこう面倒です。
全部登録しておくと認識率も下がりますし。

それと同時に分野などで辞書(タブ区切りファイル:TSV)ファイルを分割しておいて
登録する前に結合するスクリプトも用意しました。

全てのスクリプトはPythonの仮想環境(virtualenv)で動かすことを前提にしています。

```powershell
py -m venv env
.\env\Script\Activate.ps1
pip insatll -r requirements.txt
```

### `concat_dict.py`

分割された辞書(TSV)を結合するスクリプトです。
同じディレクトリにある`concat_conf.yaml`の指定に従って辞書を結合します。

結合された辞書は`out`ディレクトリ内に出力されます。
辞書が正常であるかどうかのチェックは(今のところ)していません。

```powershell
python .\concat_dict.py
```

なお`concat_conf.yaml`には`general.tsv`の指定がありますが、
こちらはリポジトリに含めていません。

これは個々人によって共通する部分が違うことを想定しているためで
あらかじめ`general/general.tsv`を作成しておいてください。

### `upload_dict.py`

辞書をAmiVoice Cloudの指定されたプロファイルに登録します。

登録するプロファイル名は辞書ファイル名の拡張子を除いた部分になります。
例えば辞書ファイル名が`ff14.tsv`であった場合、
登録されるプロファイルは`ff14`になり、
音声認識で指定するプロファイル名は`:ff14`になります。

```powershell
python .\upload_dict.py --appkey APPKEY --grammar 接続エンジン名 辞書ファイル
```

appkeyとgrammarオプションはどちらも省略可能です。
appkeyを省略する場合には`AMIVOICE_APPKEY`環境変数に使用するAPPKEYを設定してください。
grammarを省略した場合は`-a-general`(会話_汎用)が指定されたものと見なします。

辞書ファイルの指定にはワイルドカードが使用可能です。

```powershell
python .\upload_dict.py .\out\*.tsv
```

辞書ファイルの指定も省略した場合は`.\out\*.tsv`が指定されたと見なします。

### `atokdic_to_amivoicetsv.py`

ATOKのユーザー辞書用テキストファイルを
AmiVoice Cloud用のTSVファイルへ変換するスクリプトですが、
使い捨てるつもりで作ったものですので2度以上使われることは想定してません。

## 辞書

general以外の全ての辞書は`dict`ディレクトリ以下に配置されています。

### ff14

"ファイナルファンタジー XIV: 新生エオルゼア"用の辞書です。
拡張の"暁月のフィナーレ"(6.3)時点までの単語をゆるやかに収録しています。
性質上ネタバレを含みます。

辞書のエントリは
(https://signos-k-online.com/index/2017/05/21/ime%E7%94%A8ff14%E8%BE%9E%E6%9B%B8%E4%BD%9C%E6%88%90/)
から一部を移植しました。

元ゲームの著作権表示は`(C) SQUARE ENIX CO., LTD. All Rights Reserved.`になります。

### borderbreak

"BORDER BREAK"(PS4版)用の辞書です。
これも全てを収録するのではなく必要なところだけに絞って収録しています。

元ゲームの著作権表示は`©SEGA`になります。

### eternalreturn

"エターナルリターン"用の辞書です。
最新のバージョンにはついていけていません。

元ゲームの著作権表示は`©2021 Nimbleneuron Corp`になります。

# ライセンス

[CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.ja)です。

# 参考

## 汎用エンジンクラス一覧

- (クラス指定なし): 空白 or 無し
- 固有名詞
- 名前: 名前の姓(family name)
- 名前(名)： 名前の名(first name)
- 駅名
- 地名
- 会社名
- 部署名
- 役職名
- 記号
- 括弧開き
- 括弧閉じ
- 元号

[AmiVoice Tech Blogの単語登録クラス解説エントリ](https://amivoice-tech.hatenablog.com/entry/2022/10/31/155606)に
詳細が載っています。

## 読み部分あれこれ

公式のものではありませんので念のため。

- 読みには **ヴァ/ヴィ/ヴ/ヴェ/ヴォ** は使えない: **ば/び/ぶ/べ/ぼ** で入力する必要がある
- 読みの自動変換抑制には変換を抑制したい音の前に"."(半角ドット)を挿入する
- 読みは実際の発音を入力する( **は** を **わ** と表記すべき場面があるかもしれない)

どのエラーにひっかかってるか確認するには1エントリずつWebから登録して見ると良いです。

[Tech Blogに参考記事](https://amivoice-tech.hatenablog.com/entry/2022/01/13/101135)があります。
