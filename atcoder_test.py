from IPython.core import magic_arguments
from IPython.core.magic import register_line_cell_magic
import builtins
import requests
from bs4 import BeautifulSoup as bs
from io import StringIO
import sys


@magic_arguments.magic_arguments()
@magic_arguments.argument(
    '-f', "--filenames", type=str,
    help='file(s) of testcase', nargs="*"
)
@magic_arguments.argument(
    "-u", "--url", type=str, help="url of testcase")
@magic_arguments.argument(
    "-s", "--save_file_name", type=str, default=None, help="prefix of name of file to save test cases got from url")
@magic_arguments.argument(
    "content", type=str,
    help='file(s) or url', nargs="*"
)
@register_line_cell_magic
def test_input(line, cell):
    """test by change builtins.input to io.redeline(), etc...

        %%test_input [filename(s) or url] [-f filenames] | [-u url]  [-s save file name]

    optional aruments:
       -f, --filenames           : file to change builtins.input to io.readline
       -u, --url                 : atcoder url to get test case and change builtins.input to io.readline
       -s, --save_file_name      : file name to save data got from url
    """
    args = magic_arguments.parse_argstring(test_input, line)
    if args.content:
        s0: str = args.content[0]
        if s0.startswith("https://") or s0.startswith("http://"):
            _toggle_input_by_url(s0, cell, args.save_file_name)
            return
        else:
            _toggle_input_by_file_names(args.content, cell)
            return
    elif args.filenames:
        _toggle_input_by_file_names(args.filenames, cell)
        return
    elif args.url:
        _toggle_input_by_url(args.url, cell, args.save_file_name)
        return


class input_wrapper:
    def __init__(self):
        raise NotImplementedError

    def __call__(self):
        raise NotImplementedError

    def return_input(self, res):
        print("<<< {}".format(res))
        return res


class input_wrapper_from_file_name(input_wrapper):
    def __init__(self, fname):
        self.f = open(fname, "r")
        self.f = open(fname, "r")

    def __call__(self):
        return self.return_input(self.f.readline().rstrip())

    def __del__(self):
        self.f.close()


class input_wrapper_from_text(input_wrapper):
    def __init__(self, text):
        self.text = text
        self.text_io = StringIO(text)

    def __call__(self):
        return self.return_input(self.text_io.readline().rstrip())


def _toggle_input(toggle_off: bool = False, *, fname=None, text=None):
    global input
    if toggle_off:
        input = builtins.input
        return
    elif fname:
        input = input_wrapper_from_file_name(fname)
        return
    elif text:
        input = input_wrapper_from_text(text)
        return


def _read_atcoder_testcase_from_url(url):
    r = requests.get(url)
    soup = bs(r.text, "xml")
    div = soup.find_all("div", attrs={"class": "part"})
    testcases, answer = [], []
    for d in div:
        h3 = d.h3
        if h3:
            if h3.text.startswith("入力例"):
                content = d.pre.text[:-1]
                testcases.append(content)
            if h3.text.startswith("出力例"):
                content = d.pre.text[:-1]
                answer.append(content)

    return testcases, answer


def _toggle_input_by_file_names(fnames, cell):
    for fname in fnames:
        print("... test case {} ...".format(fname))
        _toggle_input(fname=fname)
        exec(cell)
        _toggle_input(toggle_off=True)
    return


def _exec_and_test(cell : str, answer : str):
    old_stdout = sys.stdout
    try:
        sys.stdout = StringIO()
        exec(cell)
    finally:
        outs = sys.stdout.getvalue()[:-1]
        sys.stdout = old_stdout
        print(outs)

    buf = [ out for out in outs.split("\n") if not(out.startswith("<<<"))]
    outs = buf
    answer = answer.split("\n")
    if len(outs) != len(answer):
        return False
    res = True
    for out, ans in zip(outs, answer):
        if out != ans:
            res = False
    return res



def _toggle_input_by_url(url, cell, save_file_name):
    testcases, answer = _read_atcoder_testcase_from_url(url)
    res = []
    for i, testcase in enumerate(testcases):
        print("... test case {} ...".format(i))
        if save_file_name:
            _toggle_input(text=testcase)
            with open(save_file_name + str(i), "w") as f:
                f.write(testcase)
        else:
            _toggle_input(text=testcase)
        r =  _exec_and_test(cell, answer[i])
        res.append(r)
        if not(r):
            print("!!! WA case{}".format(i))
            print("!!! Answer : ")
            print(answer[i])
            print("\n")

        _toggle_input(toggle_off=True)
    print("\n========== Report ==========")
    for i,r in enumerate(res):
        print("test {} : {:>10}".format(i,str(r)))
    return
