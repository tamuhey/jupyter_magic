import os
from IPython.core import magic_arguments
from IPython.core.magic import (register_line_magic, register_cell_magic, register_line_cell_magic)
import builtins


@magic_arguments.magic_arguments()
@magic_arguments.argument(
    'filename', type=str,
    help='file to write', default=None
)
@register_line_magic
def myinput(line):
    args = magic_arguments.parse_argstring(myinput, line)
    fname = os.path.expanduser(args.filename)
    global input
    if not fname:
        input = builtins.input
    elif os.path.exists(fname):
        f = open(fname, "r")

        def input_from_file():
            res = f.readline()[:-1]
            print("<<< {}".format(res))
            return res

        input = input_from_file
    else:
        print("File Not Found {}".format(fname))
        input = builtins.input


@magic_arguments.magic_arguments()
@magic_arguments.argument(
    "-s", "--separator", type=str, action="store", default="#"
)
@magic_arguments.argument(
    "prefix", type=str
)
@magic_arguments.argument(
    "-m", "--manual",  action="store_true", default="True"
)
@register_cell_magic
def testcase(line,cell):
    args = magic_arguments.parse_argstring(testcase, line)
    count = 0
    fname = "{}{}".format(args.prefix, count)
    f = open(fname, "w", encoding="utf-8")
    print("Writeing {}".format(fname))
    for l in cell.split("\n"):
        if l.startswith(args.separator):
            f.close()
            count += 1
            fname = "{}{}".format(args.prefix, count)
            f = open(fname, "w", encoding="utf-8")
            print("Writeing {}".format(fname))
        f.write(l + "\n")
    f.close()