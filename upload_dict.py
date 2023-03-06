"""
指定された辞書をAmiVoiceCloudにアップロードする
"""

import os
import typing
import glob
from typing import TextIO, Final
from pathlib import Path
import argparse
import logging
import functools
import asyncio
import websockets.client

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.INFO)
logger.addHandler(consoleHandler)


def read_tsv(source: TextIO) -> typing.List[typing.Tuple[str, str, str]]:
    """
    sourceからタブ区切り辞書ファイルを読み込んで
    それぞれの行のタプルを含んだリストを返します。
    """
    result: typing.List[typing.Tuple[str, str, str]] = list()
    for line in source:
        values = line.rstrip(" \n").split("\t")
        if not (len(values) == 2 or len(values) == 3):
            logger.warning("Cannot split line: %s", line)
            continue
        if len(values) == 2:
            result.append((values[0], values[1], ""))
        else:
            result.append((values[0], values[1], values[2]))
    return result


async def upload(
    profile_id: str,
    source: typing.List[typing.Tuple[str, str, str]],
    grammar_file_name: str = "-a-general",
    appkey: str = "",
) -> None:
    """AmiVoice CloudにWebSocketで接続して単語を登録します。

    AmiVoice Cloudに単語を登録します。
    単語登録は追加ではなくそのプロファイルの内容を全て置きかえる形になります。
    接続するのに使用するAPPKEYはワンタイムのものでもかまいません。
    使用するエンジンによっては単語登録が出来ません。

    :param profile_id: 登録したいprofileId
    :param source: read_tsvで作成された登録単語のリスト
    :param grammar_file_name: 登録する接続エンジン名
    :param appkey: 接続するのに使用するAPPKEY
    """
    S_COMMAND: Final = 's MSB16K {grammar} profileId={profile} profileWords="{words}" authorization={authorization}'

    if (not isinstance(profile_id, str)) or (len(profile_id) == 0):
        raise ValueError("profile_id is invalid.")
    if (not isinstance(grammar_file_name, str)) or (len(grammar_file_name) == 0):
        raise ValueError("grammar_file_name is invalid.")

    if (appkey == "") and ("AMIVOICE_APPKEY" in os.environ):
        appkey = os.environ["AMIVOICE_APPKEY"]
    elif len(appkey) == 0:
        raise ValueError("appkey is empty.")

    profile_id = profile_id.lstrip(":")

    logger.info("length: %d", len(source))

    register_str: str = functools.reduce(
        lambda l, r: (
            l + "|" + functools.reduce(
                lambda il, ir: il + " " + ir, r, ""
            ).strip()
        ),
        source,
        "",
    )
    s_str = S_COMMAND.format(
        grammar=grammar_file_name,
        profile=profile_id,
        words=register_str,
        authorization=appkey,
    )
    uri: Final = r"wss://acp-api.amivoice.com/v1/"

    async with websockets.client.connect(uri, logger=logger, ssl=True) as ws:
        await ws.send(s_str)
        logger.info("WS: send s, wait s")
        s_result = await ws.recv()
        if not isinstance(s_result, str):
            logger.error("WS: s error -> return binaryFrame")
            await ws.close()
        elif len(s_result) > 3:
            logger.error("WS: s error -> %s", s_result.lstrip("s "))
        else:
            logger.info("WS: recv -> %s", s_result)
            await ws.send("e")
            logger.info("WS: send e, wait e")
            while True:
                e_result = await ws.recv()
                if isinstance(e_result, str):
                    logger.info("WS: return e -> %s", e_result)
                    if e_result.strip() == "e":
                        break
                    if (len(e_result) > 2) and (e_result[0] == "e"):
                        logger.error("WS: return e -> %s", e_result)
                        break
                else:
                    logger.error("WS: e error -> return binaryFrame")
                    break


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--appkey", "-k", help="AmiVoice Cloud AppKey.", type=str, default=""
    )
    argparser.add_argument(
        "--grammar",
        "-g",
        help="AmiVoice grammar engine name (ex. '-a-general')",
        default="-a-general",
    )
    argparser.add_argument(
        "dictpath",
        nargs="*",
        help="tsv file(s) to register.",
        type=str,
        default=[r"./out/*.tsv"],
    )
    args = argparser.parse_args()
    dictpath: str = vars(args)["dictpath"]

    words_filename = [Path(f) for files in dictpath for f in glob.glob(files)]
    # print(words_filename)

    for i in words_filename:
        with open(i, mode="r", encoding="utf-8") as f:
            words = read_tsv(f)
            profile_id = i.stem
            grammar: str = vars(args)["grammar"]
            appkey: str = vars(args)["appkey"]
            logger.info("Upload -> profile: %s", profile_id)
            asyncio.run(
                upload(
                    profile_id=profile_id,
                    grammar_file_name=grammar,
                    source=words,
                    appkey=appkey,
                )
            )


if __name__ == "__main__":
    main()
