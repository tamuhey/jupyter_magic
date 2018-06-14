# Jupyter Magic Command
## install
`cp myinput.py ~/.ipython/profile_default/startup/`

## Content
### myinput.py
override builtins.input to io.TextIOWrapper.readline  
### testcase.py
read test case in cell and write to file  
### read_atcoder_testcase_from_url.py
read test case of atcoder programming challenge from url  