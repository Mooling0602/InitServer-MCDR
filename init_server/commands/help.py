## 咕咕咕，还没完成……
from mcdreforged.api.all import *


psi = ServerInterface.psi()

help_list = [
    "",
    ""
]

def get_help_page():
    help_page = RTextList(*[psi.rtr(key) + "\n" for key in help_list])
    return help_page
