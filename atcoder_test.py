from IPython.core import magic_arguments
from IPython.core.magic import register_line_cell_magic
import builtins
import requests
from bs4 import BeautifulSoup as bs
from io import StringIO


@magic_arguments.magic_arguments()
@magic_arguments.argument(
    '-f', "--filenames", type=str,
    help='file(s) of testcase', nargs="*"
)
@magic_arguments.argument(
    "-u", "--url", type=str, help="url of testcase")
@magic_arguments.argument(
    "-s", "--save_file_name", type=str, help="prefix of name of file to save test cases got from url")
@register_line_cell_magic
def test_input(line, cell):
    """test by change builtins.input to io.redeline(), etc...

        %%test_input [-f filenames] | [-u url]  [-s sava file name]

    optional aruments:
       -f, --filenames           : file to change builtins.input to io.readline
       -u, --url                 : atcoder url to get test case and change builtins.input to io.readline
       -s, --save_file_name      : file name to save data got from url
    """
    args = magic_arguments.parse_argstring(test_input, line)
    if args.filenames:
        for fname in args.filenames:
            print("... test case {} ...".format(fname))
            _toggle_input(fname=fname)
            exec(cell)
            _toggle_input(toggle_off=True)
    elif args.url:
        testcases = _read_atcoder_testcase_from_url(args.url)
        for i, testcase in enumerate(testcases):
            print("... test case {} ...".format(i))
            if args.save_file_name:
                _toggle_input(text=testcase)
                with open(args.save_file_name + str(i), "w") as f:
                    f.write(testcase)
            else:
                _toggle_input(text=testcase)
            exec(cell)
            _toggle_input(toggle_off=True)


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
    count = 0
    res = []
    for d in div:
        h3 = d.h3
        if h3:
            if h3.text.startswith("入力例"):
                content = d.pre.text[:-1]
                res.append(content)
    return res
