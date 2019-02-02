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

    def print(self, project_vars, exec_dir, local_var_values):
        mystring = self.func[2] + " "
        mystring = self.populate_global_vars(mystring, project_vars)
        for flag in self.flags:
            mystring += flag[2] + " "
        mystring = self.populate_global_vars(mystring, project_vars)
        for static in self.statics:
            mystring += static[2] + " " + exec_dir + static[3] + " "
        mystring = self.populate_global_vars(mystring, project_vars)
        #pdb.set_trace()
        for sett in self.sets:
            prefix = sett[2]
            relative = sett[3]
            selection = sett[4]
            prefix = self.populate_global_vars(prefix, project_vars)
            selection = self.populate_global_vars(selection, project_vars)
            for key in local_var_values:
                val = local_var_values[key]
                matches = re.findall(r'({.*?})', selection)
                for m in matches:
                    if m[1:-1] == key:
                        selection = selection.replace(m, val) 
            if not relative:
                mystring += prefix + " " + selection + " "
            else:
                mystring += prefix + " " + exec_dir + selection + " "
        return mystring
        
    def populate_global_vars(self, mystring, project_vars):
        # replace global variables with user values
        for var in project_vars:
            mystring = mystring.replace(var[0], var[1])
        return mystring
