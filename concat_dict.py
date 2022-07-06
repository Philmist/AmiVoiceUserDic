import sys
from pathlib import Path
from ruamel.yaml import YAML

def concat(directory_name: str, yaml_file_name: str) -> None:
    yaml = YAML()
    output_path = Path(".")
    output_path = output_path / directory_name
    with open(yaml_file_name, mode="r", encoding="utf-8") as f:
        config = yaml.load(f)
        for key, value in config.items():
            output_filename = output_path / key
            print(f"output to: {output_filename.name}")
            with open(output_filename, mode="w", encoding="utf-8") as out_file:
                for in_filename in value:
                    in_file_path = Path(".")
                    in_file_path = in_file_path / in_filename
                    with open(in_file_path, mode="r", encoding="utf-8") \
                            as in_file:
                        out_file.write(in_file.read())
                        print(f"  concat: {in_file_path.name}")


if __name__ == "__main__":
    concat("out", "concat_conf.yaml")
