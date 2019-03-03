#!/usr/bin/env python3

class Loop:

    def __init__(self, no, var, var_selection, dir_selection):
        self.no = no
        self.var = var
        self.var_selection = var_selection
        self.dir_selection = dir_selection

    def __ne__(self,o):
        if self.no != o.no:
            return True
        if self.var != o.var:
            return True
        if self.var_selection != o.var_selection:
            return True
        if self.dir_selection != o.dir_selection:
            return True
        else:
            return False
