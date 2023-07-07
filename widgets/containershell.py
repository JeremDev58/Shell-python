from baseshell import BaseShell
import typing
from tkinter import Tk


class ContainerShell(BaseShell):
    def __init__(self, root: Tk, rc: str = None, ls_func: typing.List[str] = None):
        BaseShell.__init__(self, rc, ls_func)
        self.root = root
        self.shells = []

        
