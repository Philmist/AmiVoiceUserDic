import argparse
import logging
import glob
import functools
import typing
from pathlib import Path
from ruamel.yaml import YAML
import util

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.INFO)
logger.addHandler(consoleHandler)


def concat(
    directory_name: str, yaml_file_name: str, engine_name: str = "-a-general"
) -> None:
    dict_class: typing.Union[
        None, typing.Type[util.AmiVoiceDictABC]
    ] = functools.reduce(
        lambda p, n: n if n.enginename() == engine_name else p,
        util.dict_classes,
        None
    )
    if dict_class is None:
        logger.error("Cannot find suitable grammar engine: '%s'", engine_name)
        return
    yaml = YAML()
    output_path = Path(".")
    output_path = output_path / directory_name
    with open(yaml_file_name, mode="r", encoding="utf-8") as f:
        config = yaml.load(f)
        for key, value in config.items():
            output_filename = output_path / key
            # print(f"output to: {output_filename.name}")
            logger.info("Output: %s", output_filename)
            with open(output_filename, mode="w", encoding="utf-8") as out_file:
                for in_filename in value:
                    in_file_path = Path(".")
                    in_file_path = in_file_path / in_filename
                    in_files = [Path(f) for f in glob.glob(str(in_file_path))]
                    for in_file in in_files:
                        logger.info("<- read: %s", in_file)
                        with open(in_file, mode="r", encoding="utf-8") as file:
                            dict_obj = dict_class()
                            errors = dict_obj.readdict_from_textio(file)
                            if len(errors) > 0:
                                logger.warning("<- -- Error detcted")
                                for e in errors:
                                    logger.warning("<- -- L%s: %s", e[0], e[1])
                            # out_file.write(file.read())
                            out_str = dict_obj.output_tsv()
                            out_file.write(out_str)
                            # print(f"  concat: {in_file_path.name}")


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--grammar",
        "-g",
        help="AmiVoice grammar engine name (ex. '-a-general')",
        default="-a-general",
    )
    argparser.add_argument(
        "--outputdir",
        "-o",
        help="Output directory for concatrated dictionary",
        default="out",
    )
    argparser.add_argument(
        "config",
        nargs="?",
        help="Configuration file used to concat dictionaries.",
        default="concat_conf.yaml",
    )
    args = argparser.parse_args()
    dict_class: str = vars(args)["grammar"]
    config_file: str = vars(args)["config"]
    out_dir: str = vars(args)["outputdir"]
    concat(out_dir, config_file, dict_class)


if __name__ == "__main__":
    main()
