from __future__ import annotations
from assets.default import STYLE_TAG, STYLE_SHELL, WEIGHT_FONT, LIMIT_SIZE_FONT, DEFAULT_FONT, DEFAULT_COLOR
from resources.exec import LIST_FUNC
from re import compile, IGNORECASE
from tkinter.font import families, Font
from json import loads, dumps
from resources.formats import FORMAT_JSON_COMMENT, FORMAT_JSON_MULTI_LINE, FORMAT_JSON_RC_1, FORMAT_JSON_RC_2, FORMAT_STAG, \
    FORMAT_RGB, FORMAT_FONT
from resources.tools import error
from typing import List


class BaseShell:
    def __init__(self, rc: str | None = None, ls_func: List[str] | None = None):
        self.env, self.style_tag, self.style_shell, self.alias = self.setup_rc(rc)
        self.funcs = self.setup_internal_funcs(ls_func)

    def setup_rc(self, rc=None):
        text_error = "Problème d'incomptabilité.\nVous ne pouvez pas utilisé ce logiciel."
        env = {"env_per": {"HOME": str(error("pathlib", ["Path", "home"], "ERROR", text_error)),
                           "USER": str(error("os", ["getlogin"], "ERROR", text_error)),
                           "MACHINE": str(error("socket", ["gethostname"], "ERROR", text_error)),
                           "OS": str(error("platform", ["system"], "ERROR", text_error)),
                           "CWD": str(error("os", ["getcwd"], "ERROR", text_error))},
               "env_var": {}}
        style_tag = []
        style_shell = []
        alias = {}
        if rc:
            res = self.loads_rc(rc)
        else:
            res = {"style": {"tag": STYLE_TAG, "shell": STYLE_SHELL}}
        if res.get("style") and res["style"].get("tag") and isinstance(res["style"]["tag"], list):
            result = []
            values = res["style"]["tag"]
            for i in range(len(values)):
                if FORMAT_STAG.match(values[i][0]) and len(values[i]) == 2:
                    if len(values[i][1]) > 2 or len(values[i][1]) == 0:
                        values[i][1] = [DEFAULT_COLOR, self.to_tkfont(DEFAULT_FONT, DEFAULT_FONT)]
                    elif len(values[i][1]) == 1:
                        if FORMAT_RGB.match(values[i][1][0]):
                            values[i][1] = [values[i][1][0], self.to_tkfont(DEFAULT_FONT, DEFAULT_FONT)]
                        else:
                            if FORMAT_FONT.match(values[i][1][0]):
                                values[i][1] = [DEFAULT_COLOR, self.to_tkfont(values[i][1][0], DEFAULT_FONT)]
                            else:
                                values[i][1] = [DEFAULT_COLOR, self.to_tkfont(DEFAULT_FONT, DEFAULT_FONT)]
                    else:
                        if not FORMAT_RGB.match(values[i][1][0]):
                            values[i][1][0] = DEFAULT_COLOR
                        if not FORMAT_FONT.match(values[i][1][1]):
                            values[i][1][1] = DEFAULT_FONT
                        else:
                            values[i][1][1] = self.to_tkfont(values[i][1][1], DEFAULT_FONT)
                    result.append(i)
            res["style"]["tag"] = values
            if len(result):
                for i in result:
                    style_tag.append(res["style"]["tag"][i])
            else:
                style_tag.extend(STYLE_TAG)
        else:
            style_tag.extend(STYLE_TAG)
        if res.get("style") and res["style"].get("shell") and isinstance(res["style"]["shell"], list) \
                and len(res["style"]["shell"]) == 3:
            values = res["style"]["shell"]
            if FORMAT_RGB.match(values[0]):
                style_shell.append(values[0])
            else:
                style_shell.append(STYLE_SHELL[0])
            if FORMAT_RGB.match(values[1]):
                style_shell.append(values[1])
            else:
                style_shell.append(STYLE_SHELL[1])
            style_shell.append(self.to_tkfont(values[2], STYLE_SHELL[2]))
        if res.get("env") and isinstance(res["env"], dict):
            for k, v in res["env"].items():
                if k not in env.keys() and isinstance(v, str):
                    env["env_var"].update({k: v})
        if res.get("alias") and isinstance(res["alias"], dict):
            for k, v in res["alias"].items():
                if k not in alias.keys() and isinstance(v, str):
                    alias.update({k: v})
        if not len(style_tag):
            style_tag.extend(STYLE_TAG)
        if not len(style_shell):
            style_shell.extend(STYLE_TAG)
        return env, style_tag, style_shell, alias

    def loads_rc(self, rc=None):
        if rc:
            try:
                kw = loads(self.comment_json(rc))
            except:
                return {}
            return kw
        return {}

    @staticmethod
    def comment_json(json_str: str):
        result = json_str
        while True:
            if FORMAT_JSON_MULTI_LINE.search(result):
                start, end = FORMAT_JSON_MULTI_LINE.search(result).regs[0]
                result = result.replace(result[start:end], '')
            else:
                break
        result = result.split("\n")
        while True:
            comment = False
            for i in range(len(result)):
                if FORMAT_JSON_COMMENT.search(result[i]):
                    comment = True
                    start = FORMAT_JSON_COMMENT.search(result[i]).regs[0][0]
                    result[i] = result[i][:start]
            if not comment:
                break
        return '\n'.join(result)

    @staticmethod
    def save_rc(path, dict_info):
        try:
            with open(path, 'w') as f:
                f.write('')
            kw_json = dumps(dict_info)
            ls = []
            iter1 = FORMAT_JSON_RC_1.finditer(kw_json)
            iter2 = FORMAT_JSON_RC_2.finditer(kw_json)
            for i in iter1:
                ls.append(i.span()[1])
            for i in iter2:
                ls.append(i.span()[1])
            ls.sort()
            result = ''
            count = 0
            for i in range(len(ls)):
                if count:
                    result += kw_json[count:ls[i]] + '\n'
                else:
                    result += kw_json[:ls[i]] + '\n'
                count = ls[i]
            if result != '':
                result += kw_json[count:]
                kw_json = result
            with open(path, 'a') as f:
                f.write(kw_json)
        except:
            return False
        return True

    @staticmethod
    def font_family(name_font: str, ls_fonts: list = None) -> str:
        """
        Recherche dans toutes les polices d'écriture du système une concordance et retourne la première police trouvé
        ou 'none' si aucune concordance n'a était trouvé.
        """
        if ls_fonts:
            families_font = ls_fonts
        else:
            families_font = families()
        reg_font = compile(name_font, IGNORECASE)
        for font in families_font:
            if reg_font.search(font):
                return font

        return "none"

    @staticmethod
    def setup_internal_funcs(ls_func: List[str] = None):
        result = LIST_FUNC
        if ls_func:
            for func in ls_func:
                if func not in result:
                    result.append(func)
        return result

    def analyze_font(self, font: str, ref_font: List[str]):
        if FORMAT_FONT.match(font):
            ls_font = font.split('-')
            ls_font[0] = self.font_family(ls_font[0])
            if not ls_font[1] in WEIGHT_FONT:
                ls_font[1] = ref_font[1]
            try:
                int(ls_font[2])
            except:
                ls_font[2] = ref_font[2]
            if LIMIT_SIZE_FONT[0] < int(ls_font[2]) or int(ls_font[2]) < LIMIT_SIZE_FONT[1]:
                ls_font[2] = ref_font[2]
            return '-'.join(ls_font)
        else:
            return ref_font

    def to_tkfont(self, font_str: str, default_font: str):
        """
        Convertit une string en tk.Font() et la retourne.
        FORMAT font_str: 'family-weight-size'
        FAMILY: valid family or none
        WEIGHT: bold, italic, roman, barred or none
        """
        font = self.analyze_font(font_str, default_font.split('-')).split('-')
        tkfont = Font()
        if font[0].lower() != "none":
            tkfont.configure(family=font[0])
        if font[1].lower() != WEIGHT_FONT[-1]:
            if font[1].lower() == WEIGHT_FONT[0]:
                tkfont.configure(weight=WEIGHT_FONT[0])
            if font[1].lower() == WEIGHT_FONT[1]:
                tkfont.configure(slant=WEIGHT_FONT[1])
            if font[1].lower() == WEIGHT_FONT[2]:
                tkfont.configure(slant=WEIGHT_FONT[2])
            if font[1].lower() == WEIGHT_FONT[3]:
                tkfont.configure(overstrike=1)
        tkfont.configure(size=int(font[2]))
        return tkfont
