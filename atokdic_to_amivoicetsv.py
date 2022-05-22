import fileinput
import os
import glob
import sys
from typing import List

# https://stackoverflow.com/questions/21731097/how-to-pass-wildcard-argument-like-txt-in-windows-cmd
all_files = [f for files in sys.argv[1:] for f in glob.glob(files)]

class_conversion = {"固有地名": "地名", "固有一般": "固有名詞"}

with fileinput.input(all_files, openhook=fileinput.hook_encoded("cp932")) as f:
    for line in f:
        if line.startswith("!"):
            continue
        splitted = line.split()
        if len(splitted) < 3:
            continue
        word_class = splitted[2]
        word_class = class_conversion.get(word_class, "")
        yomi = splitted[0]
        hyouki = splitted[1]
        print("{0}\t{1}\t{2}".format(hyouki, yomi, word_class))
