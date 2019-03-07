%python
import os

dir = "/aaa"

os.chdir(dir)
ls = os.popen("ls").read()
print(ls)

