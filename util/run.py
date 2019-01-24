#!/usr/bin/python3

from util.loop import *
from lib.command import Command
import re
from copy import deepcopy

import pdb

def run_module(builder, project, module):
    command = module.command
    
    # concatenate all loop dir selections giving us relative path to execution
    # directory. This is the relative path we pass to the shell at project
    # working directory
    file_sel = concat_dir_selections(command.loops)
    # get the relative path and the local_var_regexes and any other regexes in 
    # the path
    full_path, local_var_regexes, regexes = get_execution_filepath(file_sel, project.vars, command.loops)
    # build directory set
    dir_set = build_directory_set(builder, 
                                project, 
                                full_path,
                                file_sel,
                                local_var_regexes, 
                                regexes)
    # copy dictionary and populate with values of local var i.e., '{$subj}': 'SUB01'
    local_var_values = deepcopy(local_var_regexes)
    cmds = []
    for exec_dir in dir_set:
        for key in local_var_regexes:
            regex = local_var_regexes[key]
            m = re.search(regex, exec_dir)
            local_var_values[key] = m[0]
        cmds.append(command.print(exec_dir, local_var_values))
    print(cmds)
        
                
