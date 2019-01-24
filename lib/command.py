#!/usr/bin/env python\

import re
import pdb

class Command:

    def __init__(self):
        self.loops = []
        
        # command function
        self.func = [None, None, ""] 
               
        # command options
        self.flags = []
        self.statics = []   
        self.sets = []
        self.max_index = float(0)
        self.str = ""
        
    def get_max_index(self):
        """ return max index of module command so that adjustment does
            not allow the input of out-of-range indices"""
        if self.func[2] == "":
            return float(len(self.flags) + len(self.statics) + len(self.sets) - 1)
        else:
            return float(len(self.flags) + len(self.statics) + len(self.sets))

    def print(self, exec_dir, local_var_values):
        mystring = self.func[2] + " "
        for flag in self.flags:
            mystring += flag[2] + " "
        for static in self.statics:
            mystring += static[2] + " " + exec_dir + static[3] + " "
        #pdb.set_trace()
        for sett in self.sets:
            prefix = sett[2]
            selection = sett[4]
            for key in local_var_values:
                val = local_var_values[key]
                matches = re.findall(r'({.*?})', selection)
                for m in matches:
                    if m[1:-1] == key:
                        selection = selection.replace(m, val)
            mystring += prefix + " " + exec_dir + selection + " "
        return mystring
