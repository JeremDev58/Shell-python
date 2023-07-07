from __future__ import annotations
from typing import List
from re import compile, IGNORECASE
from pathlib import Path
from resources.type_sh import Shell
from os import scandir, stat
from stat import filemode
from time import ctime
from resources.tools import Table


LIST_FUNC = ["rgb", "degrade", "cd", "ls"]


def rgb(rgb_color: str, error=True) -> bool:
    """Controle le format de la couleur passer en paramètre.
       FORMAT: string ex: #123456"""
    format_rgb = compile('^[#][a-f0-9]{6}$', IGNORECASE)
    if format_rgb.match(rgb_color) and len(rgb_color) == 7:
        return True
    return False


rgb.help = "Controle le format de la couleur passer en paramètre. FORMAT: string ex: #123456"
rgb.param = "-r or -rgb: str"


def degrade(shell: Shell | None, color: str, color_num: int = 1, step: int = 20) -> List[str]:
    """Degrade prend une couleur et retourne une palette de couleur dégradé."""
    if color_num <= 0:
        if shell is None:
            raise ValueError("ERROR: f:degrade() p:color_num \n La valeur de color_num ne peut pas inférieur ou égal a 0.")
        else:
            shell.display("ERROR: f:degrade() p:color_num \n La valeur de color_num ne peut pas inférieur ou égal a 0.")
    if step < 0:
        if step / color_num < -255 / color_num:
            if shell is None:
                raise ValueError("ERROR: f:degrade() p:step \n La valeur de step ne peut être inférieur a " +
                             str(-255 / color_num) + " ou supérieur a " + str(255 / color_num) +
                             " avec color_num qui est égal a " + str(color_num) + ".")
            else:
                shell.display("ERROR: f:degrade() p:step \n La valeur de step ne peut être inférieur a " +
                             str(-255 / color_num) + " ou supérieur a " + str(255 / color_num) +
                             " avec color_num qui est égal a " + str(color_num) + ".")
    elif step > 0:
        if step / color_num > 255 / color_num:
            if shell is None:
                raise ValueError("ERROR: f:degrade() p:step \n La valeur de step ne peut être inférieur a " +
                             str(-255 / color_num) + " ou supérieur a " + str(255 / color_num) +
                             " avec color_num qui est égal a " + str(color_num) + ".")
            else:
                shell.display("ERROR: f:degrade() p:step \n La valeur de step ne peut être inférieur a " +
                             str(-255 / color_num) + " ou supérieur a " + str(255 / color_num) +
                             " avec color_num qui est égal a " + str(color_num) + ".")
    else:
        if shell is None:
            raise ValueError("ERROR: f:degrade() p:step \n La valeur de step ne peut être égal a 0.")
        else:
            shell.display("ERROR: f:degrade() p:step \n La valeur de step ne peut être égal a 0.")
    rgb(color)
    ls_color = []
    for n in range(0, color_num):
        subcolor = '#'
        for i in range(0, 7):
            if i != 0:
                if i % 2 == 0:
                    str_to_hex = "0x" + color[i - 1] + color[i]
                    hex_to_int = int(str_to_hex, 16)
                    hex_to_int += step
                    if hex_to_int <= 0:
                        int_to_hex = hex(0)
                        if len(int_to_hex) < 4:
                            int_to_hex += "0"
                    elif hex_to_int >= 255:
                        int_to_hex = hex(255)
                    else:
                        int_to_hex = hex(hex_to_int)
                    subcolor += int_to_hex[2:]
        color = subcolor
        ls_color.append(subcolor)
    return ls_color


degrade.pyshell = {"info_func": "Degrade prend une couleur et retourne une palette de couleur dégradé.",
                   "info_param": "Paramètre:\n"
                                 "\t-c or -color: str  |  String au format: #123456\n"
                                 "\t-n or -num: int = 1  |  Nombre de de couleur renvoyer.\n"
                                 "\t-s or -step: int = 20  |  Nombre enlever ou rajouter a la couleur.",
                   "name_param": {"abr": ["-c", "-n", "-s"], "real": ["-color", "-num", "-step"], "values": [str, int, int]},
                   "type_param": dict,
                   "len_param": {"min": 1, "max": 3}}


def cd(shell: Shell, *args):
    params = args[0]
    print(params)
    if params is None:
        shell.display("Un chemin doit être passée a cd.")
        return
    if isinstance(params, list) and len(params) > 1:
        shell.display("cd ne prend qu'un seul paramètre.")
        return
    pathout = str(params)
    if '~' in pathout:
        pathout = pathout.replace('~', str(shell.env["env_per"]["HOME"]))
    p = Path(pathout)
    if p.is_absolute():
        if not p.exists():
            shell.display("Le chemin passée n'éxiste pas.")
            return
        shell.cwd = str(p)
    else:
        path_resolve = Path(shell.cwd).joinpath(pathout)
        print(path_resolve)
        if not path_resolve.exists():
            shell.display("Le chemin passée n'éxiste pas.")
            return
        shell.cwd = str(path_resolve.resolve())


cd.pyshell = {"info_func": "cd permet de ce déplacer dans les dossiers de l'OS.",
              "info_param": "\nParamètre:\n"
                            "\tpath/relatif: str  |  String au format: chemin/relatif/du/dossier.\n"
                            "\tpath/absolute: str  |  String au format: racine/chemin/absolute/du/dossier.\n",
              "type_param": str}


def ls(shell: Shell, *args):
    params = args[0]
    if params is None:
        params = {"-i": False, "-o": False, "-s": False, "-m": False, "-a": False}
    lst_st = []
    files = []
    cwd = shell.cwd
    for ent in scandir(cwd):
        pth = "{}/{}".format(cwd, ent.name)
        p = Path(pth)
        stats = stat(pth)
        files.append([str(stats.st_ino), filemode(stats.st_mode), str(stats.st_size),
                      ctime(stats.st_mtime), ctime(stats.st_atime), ent.name])
        if "win" not in shell.env["env_per"]["OS"].lower():
            files[-1].append(p.owner())
            files[-1].append(p.group())
    if params["-i"]:
        lst_st.append(["inode"])
        for st in files:
            lst_st[-1].append(st[0])
    if params["-o"]:
        lst_st.append(["Mode"])
        for st in files:
            lst_st[-1].append(st[1])
        if "win" not in shell.env["env_per"]["OS"].lower():
            lst_st.append(["Owner"])
            for st in files:
                lst_st[-1].append(st[6])
            lst_st.append(["Group"])
            for st in files:
                lst_st[-1].append(st[7])
    if params["-s"]:
        lst_st.append(["Size"])
        for st in files:
            lst_st[-1].append(st[2])
    if params["-m"]:
        lst_st.append(["Date modif"])
        for st in files:
            lst_st[-1].append(st[3])
    if params["-a"]:
        lst_st.append(["Date acces"])
        for st in files:
            lst_st[-1].append(st[4])
    lst_st.append(["Name"])
    for st in files:
        lst_st[-1].append(st[5])
    shell.display("total(" + str(len(files)) + ")")
    shell.display(Table(shell, lst_st, ignore_index=[0]).get())
    print(Table(shell, lst_st, ignore_index=[5]).get())


ls.pyshell = {"info_func": "ls permet de lister les fichiers et les dossiers et leurs informations, d'un répertoire.",
              "info_param": "Paramètre:\n"
                            "\t-i or -inode: bool | Affiche les inodes\n"
                            "\t-o or -owner: bool\n | Affiche les propriétaires, groupes et mode"
                            "\t-s or -size: bool\n | Affiche la taille"
                            "\t-m or -modif: bool\n | Affiche la date de dernière modification"
                            "\t-a or -acces: bool\n | | Affiche la date du dernier acces",
              "name_param": {"abr": ["-i", "-o", "-s", "-m", "-a"], "real": ["-inode", "-owner", "-size", "-modif", "-acces"],
                             "values": [bool, bool, bool, bool, bool]},
              "type_param": dict,
              "len_param": {"min": 0, "max": 5}}
