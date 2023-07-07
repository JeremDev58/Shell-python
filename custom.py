from tkinter import Text, Tk
from os import getcwd, getlogin
from os.path import join, exists
from json import loads
from socket import gethostname
from platform import system
from datetime import datetime
from resources.formats import *
from resources.exec import *
from widgets.shell import Shell


class MainWindow(Tk):
    ENV = {
        "HOME": Path.home(),
        "USER": getlogin(),
        "MACHINE": gethostname(),
        "OS": system(),
        "CWD": getcwd()
    }
    ENV_USER = {}
    # Stag
    STAG = ["/u", "/U", "/p", "/P", "/d", "D", "/t", "/T"]
    STAG_VAR = ["/p", "/P", "/d", "D", "/t", "/T"]
    # Date / Heure
    DATETIME = datetime
    YEAR = DATETIME.now().year
    MONTH = DATETIME.now().month
    DAY = DATETIME.now().day
    HOUR = DATETIME.now().hour
    MINUTE = DATETIME.now().minute
    SECOND = DATETIME.now().second
    # Default Style

    DEFAULT_TAG_SHELL_COLOR = "#24f578"
    DEFAULT_TAG_SHELL_FONT = "none-bold-10"
    DEFAULT_TAG_SHELL = [
        ["/u", ["#124578", "Orbitron-bold-10"]],
        ["/c[", ["#a5a7a4"]],
        ["/T", ["#e51418"]],
        ["/c]", ["#a5a7a4"]],
        ["/c:", ["#a5a7a4"]],
        ["/p", ["#88d8b0"]],
        ["/c > ", ["#f0f0f0"]]
    ]

    DEFAULT_SHELL_BG = "#060606"
    DEFAULT_SHELL_FG = "#f0f0f0"
    DEFAULT_SHELL_FONT = "None-None-9"
    LIMIT_SIZE_FONT = (60, 2)
    WEIGHT_FONT = ["bold", 'italic', "roman", "barred", "none"]

    def __init__(self):
        Tk.__init__(self)
        self.geometry("600x400")
        self.title("PyShell")
        # Attribute
        self.bin = None if not exists(join(getcwd(), "bin")) else join(getcwd(), "bin")
        self.rc = None if not exists(join(getcwd(), "pyshell.rc")) else join(getcwd(), "pyshell.rc")
        self.ERROR = []
        self.tag_shell = None
        self.init_tag_shell()
        # Window
        self.tag = None
        self.shell = Shell(self, self.tag_shell, self.ERROR)
        self.shell.pack(fill='both', expand=True)

    def init_tag_shell(self):
        if self.rc is None:
            self.tag_shell = self.DEFAULT_TAG_SHELL
        else:
            file = ""
            try:
                with open(self.rc) as f:
                    for line in f.readlines():
                        file += line
            except:
                self.ERROR.append("ERROR File: Le fichier \'pyshell.rc\' n'a pas pu être ouvert.\n")
                self.tag_shell = self.DEFAULT_TAG_SHELL
            else:
                try:
                    rc = loads(file)
                except:
                    self.ERROR.append("ERROR Json: Le fichier \'pyshell.rc\' n'a pas pu être convertis.")
                    self.tag_shell = self.DEFAULT_TAG_SHELL
                else:
                    str_shell = None if "tag_shell" not in rc else rc["tag_shell"]
                    if isinstance(str_shell, list) & str_shell:
                        self.tag_shell = rc["tag_shell"]
                    else:
                        self.tag_shell = self.DEFAULT_TAG_SHELL


