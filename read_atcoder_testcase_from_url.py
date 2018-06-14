import os
import requests
from bs4 import BeautifulSoup
from IPython.core import magic_arguments
from IPython.core.magic import (register_line_magic, register_cell_magic, register_line_cell_magic)
import builtins


@magic_arguments.magic_arguments()
@magic_arguments.argument(
    'url', type=str,
     default=None
)
@magic_arguments.argument(
    '-p', "--prefix", 
     default="test"
)
@register_line_magic
def read_atcoder_testcase_from_url(line):
    args = magic_arguments.parse_argstring(read_atcoder_testcase_from_url, line)
    r = requests.get(args.url)
    soup = bs(r.text, "xml")
    div = soup.find_all("div", attrs={"class":"part"})
    count = 0
    for d in div:
        h3 = d.h3
        if h3:
            if h3.text.startswith("入力例"):
                content = d.pre.text[:-1]
                with open("{}{}".format(args.prefix, count), "w") as f:
                    f.write(content)
                count += 1