from __future__ import annotations

from tkinter import Text
from widgets.baseshell import BaseShell
from assets.default import STAG_VAR, STAG_PER
import typing
from datetime import datetime
from re import compile
from resources.formats import FORMAT_ENV, FORMAT_COMMAND, FORMAT_ENV_DECLARE, FORMAT_ENV_CALL, FORMAT_ENV_SEARCH, \
    FORMAT_STR_SIMPLE, FORMAT_STR_HARD, FORMAT_DICT
from resources.exec import *


class Shell(Text, BaseShell):
    TAG_INIT = []
    SYM_RESERVED = ["$", "\""]

    def __init__(self, master, rc: str = None, ls_func: typing.List[str] = None):
        Text.__init__(self, master=master, spacing2=10)
        BaseShell.__init__(self, rc, ls_func)
        self.configure(background=self.style_shell[0], foreground=self.style_shell[1], font=self.style_shell[2],
                       insertbackground="#98d4e2", insertwidth=4)
        self.cwd = self.env["env_per"]["HOME"]
        self.valid_zone = [0, 0]
        self.tag_shell = self._init_tag_shell()
        self._setup_tag(True)
        self.info = "\n  Faites COMMAND -h ou -help pour avoir des infos sur les paramètres de la commande." \
                    "\n  Faite 'help' pour avoir des infos sur les commandes"

        self.bind("<BackSpace>", lambda evt: self._back_space(evt))
        self.bind("<Return>", lambda evt: self._enter(evt))
        self.bind("<Button-1>", lambda evt: self._clic(evt))
        self.bind("<Key>", lambda evt: self._key_press(evt))

    def _init_tag_shell(self):
        if not len(Shell.TAG_INIT):
            for i in range(len(self.style_tag)):
                Shell.TAG_INIT.append(["tag" + str(i), self.style_tag[i][0], self.style_tag[i][1][0],
                                       self.style_tag[i][1][1]])
        return Shell.TAG_INIT

    def _setup_tag(self, begin=False):
        if not begin:
            self.insert('end', '\n')
        for i in range(len(self.tag_shell)):
            if self.tag_shell[i][1] in STAG_VAR:
                if self.tag_shell[i][1] == STAG_VAR[0]:
                    reg = compile(self.env["env_per"]["HOME"])

                    if reg.match(self.cwd):
                        self.insert('end', "~" + self.cwd[reg.match(self.cwd).span()[1]:], self.tag_shell[i][0])
                    else:
                        self.insert('end', str(self.cwd), self.tag_shell[i][0])
                    self.tag_configure(self.tag_shell[i][0], foreground=self.tag_shell[i][2],
                                       font=self.tag_shell[i][3])
                if self.tag_shell[i][1] == STAG_VAR[1]:
                    self.insert('end', self.cwd, self.tag_shell[i][0])
                    self.tag_configure(self.tag_shell[i][0], foreground=self.tag_shell[i][2],
                                       font=self.tag_shell[i][3])
                if self.tag_shell[i][1] == STAG_VAR[2]:
                    self.insert('end', datetime.now().strftime("%d/%m/%Y"), self.tag_shell[i][0])
                    self.tag_configure(self.tag_shell[i][0], foreground=self.tag_shell[i][2],
                                       font=self.tag_shell[i][3])
                if self.tag_shell[i][1] == STAG_VAR[3]:
                    self.insert('end', datetime.now().strftime("%A %d %B, %Y"), self.tag_shell[i][0])
                    self.tag_configure(self.tag_shell[i][0], foreground=self.tag_shell[i][2],
                                       font=self.tag_shell[i][3])
                if self.tag_shell[i][1] == STAG_VAR[4]:
                    self.insert('end', datetime.now().strftime("%H:%M"), self.tag_shell[i][0])
                    self.tag_configure(self.tag_shell[i][0], foreground=self.tag_shell[i][2],
                                       font=self.tag_shell[i][3])
                if self.tag_shell[i][1] == STAG_VAR[5]:
                    self.insert('end', datetime.now().strftime("%H:%M:%S"), self.tag_shell[i][0])
                    self.tag_configure(self.tag_shell[i][0], foreground=self.tag_shell[i][2],
                                       font=self.tag_shell[i][3])
            elif self.tag_shell[i][1] in STAG_PER:
                if self.tag_shell[i][1] == STAG_PER[0]:
                    self.insert('end', self.env["env_per"]["USER"], self.tag_shell[i][0])
                    self.tag_configure(self.tag_shell[i][0], foreground=self.tag_shell[i][2],
                                       font=self.tag_shell[i][3])
                if self.tag_shell[i][1] == STAG_PER[1]:
                    self.insert('end', self.env["env_per"]["MACHINE"], self.tag_shell[i][0])
                    self.tag_configure(self.tag_shell[i][0], foreground=self.tag_shell[i][2],
                                       font=self.tag_shell[i][3])
            else:
                self.insert('end', self.tag_shell[i][1].replace("/c", ''), self.tag_shell[i][0])
                self.tag_configure(self.tag_shell[i][0], foreground=self.tag_shell[i][2],
                                   font=self.tag_shell[i][3])
        self._edit_zone()

    def _edit_zone(self) -> None:
        end = self.index("insert").split('.')
        self.valid_zone[0] = int(end[0])
        self.valid_zone[1] = int(end[1])

    def display(self, text: str) -> None:
        self.insert('end', '\n' + text)

    # COMMAND
    def execute(self, command):
        err = "Les paramètres passées ne sont pas valide." + self.info
        cmd, params = self._sort_cmd(command)
        if cmd is not None and not isinstance(params, bool):
            if FORMAT_ENV.match(cmd) and params is None:
                self._handle_env(cmd)
            elif params is not None and len(params) == 1 and (params[0] == '-help' or params[0] == '-h'):
                self.display(globals()[cmd].pyshell["info_func"] + globals()[cmd].pyshell["info_param"])
            else:
                if params is None:
                    if globals()[cmd].pyshell.get("min") != 0:
                        globals()[cmd](self, params)
                    else:
                        self.display("Au moins 1 paramètre doit être passées a la fonction." + self.info)
                else:
                    params = self._param(cmd, params)
                    print(params)
                    if params:
                        globals()[cmd](self, params)
        elif isinstance(params, bool):
            self.display(err)
        else:
            self.display("Commande introuvable.\n  Faite 'help' pour avoir des infos sur les commandes")

    def _sort_cmd(self, command: str):
        cmd = ''
        params = []
        if FORMAT_ENV.match(command):
            if FORMAT_ENV_DECLARE.match(command):
                start, end = FORMAT_ENV_DECLARE.match(command).regs[0]
                cmd += command[start:end - 1]
                params = self._clean_list(self._param_cmd(command[end:]))
                if isinstance(params, list) and len(params) != 0:
                    params = False
            elif FORMAT_ENV_CALL.match(command):
                cmd += command
        elif FORMAT_COMMAND.match(command):
            cmd += command.split(' ')[0]
            if cmd.lower() not in self.funcs:
                return None, None
            command = command.replace(command[:len(cmd)], '')
            params = self._param_cmd(command)
        params = self._clean_list(params)
        if not len(cmd):
            cmd = None
        return cmd, params

    @staticmethod
    def _clean_list(ls):
        if isinstance(ls, list):
            for el in ls:
                if el == '':
                    ls.remove(el)
            if not len(ls):
                return None
        return ls

    @staticmethod
    def _param_cmd(text: str):
        ls_param = []
        while FORMAT_STR_HARD.search(text) or FORMAT_STR_SIMPLE.search(text):
            if FORMAT_STR_HARD.search(text):
                start, end = FORMAT_STR_HARD.search(text).regs[0]
                ls_param.append(text[start:end])
                if not (len(text) - 1 == end):
                    try:
                        if text[end] != ' ':
                            return False
                    except IndexError:
                        pass
                text = text.replace(text[start:end], '')
            else:
                start, end = FORMAT_STR_SIMPLE.search(text).regs[0]
                ls_param.append(text[start:end])
                if not (len(text) - 1 == end):
                    try:
                        if text[end] != ' ':
                            return None
                    except IndexError:
                        pass
                text = text.replace(text[start:end], '')
        return ls_param

    def _param(self, cmd: str, lst: list):
        """ type str = 1 seul paramètre
            type list = plusieurs string
            type dict = plusieur paramètre """
        if globals()[cmd].pyshell["type_param"] == str:
            if len(lst) > 1:
                self.display("Trop de paramètres passées a la fonction." + self.info)
                return False
            else:
                return lst[0]
        else:
            if len(lst) < globals()[cmd].pyshell["len_param"].get("min"):
                self.display("Au moins " + str(globals()[cmd].pyshell["len_param"].get("min")) +
                             " paramètre doit être passées a la fonction." + self.info)
                return False
            elif len(lst) > globals()[cmd].pyshell["len_param"].get("max"):
                self.display("Trop de paramètres passées a la fonction." + self.info)
                return False
            is_dict = False
            for el in lst:
                if FORMAT_DICT.match(el):
                    is_dict = True
            if not is_dict and globals()[cmd].pyshell["type_param"] == list:
                return lst
            else:
                kwargs = {}
                print(lst)
                print(lst[0])
                if len(lst) == 1 and len(lst[0]) > 2 and FORMAT_DICT.match(lst[0]):

                    ls_param = []
                    string = lst[0][1:]
                    for c in string:
                        ls_param.append("-" + c)
                    for el in ls_param:
                        if el not in globals()[cmd].pyshell["name_param"]["abr"]:
                            return False
                        else:
                            kwargs.update({el: True})
                    for el in globals()[cmd].pyshell["name_param"]["abr"]:
                        if el not in ls_param:
                            kwargs.update({el: False})
                    return kwargs
                else:
                    if not FORMAT_DICT.match(lst[0]):
                        kwargs.update({globals()[cmd].pyshell["name_param"]["abr"][0]: lst[0]})
                        lst.pop(0)
                    else:
                        print("la")
                        abr = globals()[cmd].pyshell["name_param"]["abr"]
                        real = globals()[cmd].pyshell["name_param"]["real"]
                        count = 0
                        while count < len(lst):
                            if not FORMAT_DICT.match(lst[count]) and lst[count] not in abr and lst[count] not in real:
                                return False
                            else:
                                try:
                                    lst[count + 1]
                                except IndexError:
                                    kwargs.update({lst[count]: True})
                                    count += 1
                                else:
                                    if not FORMAT_DICT.match(lst[count + 1]):
                                        kwargs.update({lst[count]: lst[count + 1]})
                                        count += 2
                                    else:
                                        kwargs.update({lst[count]: True})
                                        count += 1
                        for i in range(len(abr)):
                            if abr[i] not in kwargs.keys() and real[i] not in kwargs.keys():
                                kwargs.update({abr[i]: False})
                    print(kwargs)
                    return kwargs

    # ENV
    def _handle_env(self, cmd: str):
        if FORMAT_ENV_CALL.match(cmd):
            call = cmd[1:]
            if call == "ENV":
                self.get_env()
            elif self.env["env_per"].get(call):
                self.display(self.env["env_per"][call])
            elif self.env["env_var"].get(call):
                self.display(self.env["env_var"][call])
            else:
                self.display("La variable d'environnement " + cmd + " n'éxiste pas.")
        elif FORMAT_ENV_DECLARE.match(cmd):
            declare = cmd[1:].split('=')
            self.set_env(declare[0], declare[1])
        else:
            self.display("Erreur inconnu.")

    def get_env(self):
        result = []
        for env, value in self.env["env_per"].items():
            result.append(env + "=" + value)
        if len(self.env["env_var"]):
            for env, value in self.env["env_var"].items():
                result.append(env + "=" + value)
        self.display("total(" + str(len(result)) + ")")
        for el in result:
            self.display(el)

    def set_env(self, env, value):
        for k in self.env["env_per"].keys():
            if env == k:
                self.display("La variable d'environnement $" + env + " ne peux pas être redéfinit.")
                return
        value = self.search_env(value)
        for k in self.env["env_var"].keys():
            if env == k:
                self.env["env_var"][k] = value
                self.display(k + "=" + value)
                return
        self.env["env_var"].update({env, value})

    def search_env(self, value: str) -> str:
        while FORMAT_ENV_SEARCH.search(value):
            start, end = FORMAT_ENV_SEARCH.search(value).regs[0]
            if self.env['env_per'].get(value[start + 1:end]) or self.env['env_var'].get(value[start + 1:end]):
                if self.env['env_per'].get(value[start + 1:end]):
                    value = value.replace(value[start:end], str(self.env['env_per'][value[start + 1:end]]))
                else:
                    value = value.replace(value[start:end], str(self.env['env_var'][value[start + 1:end]]))
            else:
                break
        return value

    # EVENT
    def _back_space(self, event):
        cur = self.index("insert").split(".")
        if int(cur[0]) >= self.valid_zone[0] and int(cur[1]) > self.valid_zone[1]:
            self.delete("current -1 chars", "current")
        return "break"

    def _enter(self, event, exe=True):
        command = str(self.get('{}.{}'.format(self.valid_zone[0], self.valid_zone[1]), "end"))[:-1]
        if exe and command != '':
            self.execute(command)
        self._setup_tag()
        self._edit_zone()
        self.mark_set('insert', "{}.{}".format(self.valid_zone[0], self.valid_zone[1]))
        self.yview("end")
        return "break"

    def _clic(self, event):
        self.mark_set('insert', self.index("current"))

    def _key_press(self, event):
        cur = self.index("insert").split(".")
        if not (int(cur[0]) < self.valid_zone[0]) and not \
                (int(cur[0]) == self.valid_zone[0] and int(cur[1]) < self.valid_zone[1]):
            self.insert("insert", event.char)
        return "break"
