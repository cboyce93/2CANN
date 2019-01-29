#!/usr/bin/env python3

from gi.repository import GLib, Gtk, GObject

from util.loop import *
from lib.command import Command
import re
from copy import deepcopy
import threading
import time

import pdb

def update_terminal(args):
    cp = args[0]
    textview = args[1]
    buff = args[2]
    start = time.time()
    timer = start
    output = ""
    
    while timer < start + 0.01:
        out = cp.stderr.read(1) # AFNI always erroring for some reason
        # EOF reached
        if out == '' and cp.poll() != None:
            return False
        if out != '':
            output+=str(out.decode("utf-8") )
        timer = time.time()
    # update buffer
    buff.insert_at_cursor(output, -1)
    textview.scroll_to_iter(buff.get_end_iter(), 0.1, True, 1, 1)
    if cp.poll() is not None:
        return False # destroy GLib reference
    else:
        return True

def execute_cmd(builder, cmds, textview, buff, prj_cwd):
    for i, cmd in enumerate(cmds):
        print("COMMAND "+str(i)+": " + cmd)
        cp = SP.Popen([cmd], stdout=SP.PIPE, stderr=SP.PIPE, shell=True, cwd=prj_cwd)        
        # poll till process terminates
        GLib.timeout_add(500, update_terminal, (cp, textview, buff))
        cp.wait() 

def generate_cmds(builder, project, module):
    """ Return array of shell commands to be executed """
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
    return cmds  

def run_test(builder, project, module):
    cmds = generate_cmds(builder, project, module)    
    terminal = builder.get_object('file_selection_viewer')
    textview = builder.get_object('file_selection_textview')
    builder.get_object('fsv_header').set_title('Run Test')
    builder.get_object('fsv_header').set_subtitle(module.name + '.mod')
    terminal.show()
    buff = builder.get_object('file_selection_buffer')
    # clear buffer
    buff.set_text("",-1)
    prj_cwd = project.working_directory
    thread = threading.Thread(target=execute_cmd, args=(builder, cmds, textview, buff, prj_cwd))
    thread.daemon = True
    thread.start()

def get_loop_file_selection(builder, project, module):
    builder.get_object('fsv_header').set_title('Loop File Selection')
    builder.get_object('fsv_header').set_subtitle(module.name)
    cmds = generate_cmds(builder, project, module)
    string = ""
    for cmd in cmds:
        string += cmd + "\n"
    return string

   
                
