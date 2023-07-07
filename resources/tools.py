from __future__ import annotations
from typing import List, overload
from resources.type_sh import Shell
from tkinter import messagebox



def display_of(obj: Shell | None, text: str | Exception) -> object:
    if obj is not None:
        if type(text) is not str:
            obj.display(text.args[0])
        else:
            obj.display(text)
    else:
        if type(text) is not str:
            raise text
        else:
            raise RuntimeError(text)



@overload
def error(module: str, fromlist: List[str], default_return: str = None) -> object: ...
@overload
def error(module: str, fromlist: List[str], title_error: str = None, text_error: str = None) -> object: ...
@overload
def error(module: str, fromlist: List[str], shell: Shell = None, text_error: str = None) -> object: ...


def error(module: str, fromlist: List[str], default_return: str = None, shell: Shell = None, title_error: str = None,
          text_error: str = None) -> object:
    mod = __import__(module)
    if len(fromlist) == 1:
        try:
            return getattr(mod, fromlist[0])()
        except:
            if default_return:
                return default_return
            if isinstance(shell, type(Shell)):
                display_of(shell, text_error)
                return
            if title_error:
                messagebox.showerror(title_error, text_error)
                quit()
            print("ERROR param: f:error() trop de paramètre passée à 'fromlist'.")
    elif len(fromlist) == 2:
        try:
            obj = getattr(mod, fromlist[0])
            return getattr(obj, fromlist[1])()
        except:
            if default_return:
                return default_return
            if isinstance(shell, type(Shell)):
                display_of(shell, text_error)
                return
            if title_error:
                messagebox.showerror(title_error, text_error)
                quit()
            print("ERROR param: f:error() trop de paramètre passée à 'fromlist'.")
    else:
        raise AttributeError("Trop de valeurs dans 'fromlist'.")
    
    
class Table:
    def __init__(self, root: Shell | None, lst: List[List[str]], **kwargs):
        """ Permet de créer un tableau en string.
        Exemple:    \ncolumn1 column2 column3
                    row1      row1     row1\n
                    row2      row2     row2\n\n
        Param:\n
        SPACING est le nombre minimum d'espace entre chaque celule. Defaut: 2\n
        ORDER est True quand on lui passe list de row et False quand c'est une list de column. Defaut: True\n
        WORD_REPLACE est le mot qui va être inseré dans les celule manquante. Defaut: \"\"\n
        SORT_ALPHA est un tuple avec un boolean et un index, il permet de trier par ordre alphabétique la liste a partir d'un index
        ex: list[list[index]]\n
        IGNORE_INDEX est une liste d'index a ignoré pendant le trie."""
        self.lst = lst
        spacing = 2 if not kwargs.get("spacing") else int(kwargs.get("spacing"))
        order = True if not kwargs.get("order") else bool(kwargs.get("spacing"))
        word_replace = "" if not kwargs.get("word_replace") else str(kwargs.get("spacing"))
        sort_alpha = (True, 0) if not kwargs.get("sort_alpha") else (bool(kwargs.get("sort_alpha")[0]),
                                                                     int(kwargs.get("sort_alpha")[1]))
        ignore_in = [] if not kwargs.get("ignore_index") else list(kwargs.get("ignore_index"))
        self.replace_none(self.lst, word_replace)
        if not order:
            self.lst = self.column_to_row(self.lst)
        if sort_alpha[0]:
            self.lst = self.sort_tab(lst, sort_alpha[1], ignore_in)
        self._tab = ''
        row = len(lst[0])
        column = len(lst)
        word_len_max = self._space_size(self.lst, row, column, spacing, order)
        for j in range(row):  # taille row
            for i in range(column):  # taille colonne
                space = ''
                while len(space) != (word_len_max[i]-len(self.lst[i][j])):
                    space += ' '
                self._tab += self.lst[i][j] + space
            self._tab += '\n'
    def _space_size(self, lst, first_index, second_index, spacing, order):
        size = []
        if order:
            f_in = first_index
            s_in = second_index
        else:
            f_in = second_index
            s_in = first_index
        for f in range(s_in):
            count = 0
            for s in range(f_in):
                if len(lst[f][s]) > count:
                    count = len(lst[f][s])
            size.append(count + spacing)
        return size

    @staticmethod
    def column_to_row(lst):
        ls_sorted = []
        for iter in range(len(lst[0])):
            ls_sorted.append([])
            for i in range(len(lst)):
                ls_sorted[-1].append(lst[i][iter])
        return ls_sorted

    @staticmethod
    def replace_none(lst: List[List[str]], word: str):
        """Recherche des cellule manquante et les remplace par le param word."""
        ref = len(lst[0])
        while True:
            ref_of_ref = ref
            for iter in range(len(lst)):
                if len(lst[iter]) > ref:
                    for i in range(len(lst[iter]) - ref):
                        lst[0].append(word)
                        ref += 1
                elif len(lst[iter]) < ref:
                    for i in range(ref - len(lst[iter])):
                        lst[iter].append(word)
            if ref_of_ref == ref:
                break
        return lst

    @staticmethod
    def sort_tab(lst: List[List[str]], ref_index: int, ignore_index=[], order=True):
        ls = []
        ls_sorted = []
        ref = []
        ls.extend(lst[ref_index])
        for iter in ignore_index:
            ls.pop(iter)
        ls.sort(key=lambda x: x.lower())
        for iter in range(len(ls)):
            count = 0
            while ls[iter] != lst[ref_index][count]:
                count += 1
            ref.append(count)
        for iter in ignore_index:
            ref.insert(iter, iter)
        for i in range(len(lst)):
            ls_sorted.append([])
            for index in ref:
                ls_sorted[-1].append(lst[i][index])
        return ls_sorted

    def get(self):
        return self._tab


def rgba(t_rgba: tuple):
    if len(t_rgba) != 4:
        return False
    for el in t_rgba:
        if not (isinstance(el, int) and 255 >= el >= 0):
            return False
    return True


def h_kw(kw: dict, value_dict: str, default_value, strict: bool = True):
    if strict:
        return kw[value_dict] if kw.get(value_dict) is not None and isinstance(kw.get(value_dict),
                                                                               type(default_value)) else default_value
    else:
        return kw[value_dict] if kw.get(value_dict) is not None else default_value


def del_kw(kw: dict, *args):
    for el in args:
        if kw.get(el):
            del kw[el]
    if len(kw) != 0:
        key_error = ''
        for el in kw.keys():
            key_error += "'" + str(el) + "' "
        raise AttributeError(key_error + "Ne sont pas des paramètres valide.")








