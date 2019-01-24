#!/usr/bin/python3

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
    terminal = args[1]
    buff = args[2]
    start = time.time()
    timer = start
    output = buff.get_text(buff.get_start_iter(), buff.get_end_iter(), False)
    while timer < start + 0.01:
        out = cp.stderr.read(1)
        # EOF reached
        if out == '' and p.poll() != None:
            return False
        if out != '':
            output+=str(out.decode("utf-8") )
        timer = time.time()
    buff.set_text(output, -1)
    return True

def execute_cmd(cmds, terminal, buff, prj_cwd):
    for i, cmd in enumerate(cmds):
        print("COMMAND "+str(i)+": " + cmd)
        #cp = SP.run([cmd], stdout=SP.PIPE, stderr=SP.PIPE, shell=True, cwd=project.working_directory)
        cp = SP.Popen([cmd], stdout=SP.PIPE, stderr=SP.PIPE, shell=True, cwd=prj_cwd)        
        # poll till process terminates
        GLib.timeout_add(200, update_terminal, (cp, terminal, buff))
        cp.wait()

        """
        if cp.returncode != 0:
            # pop up warning dialog for non zero return code
            stderr = cp.stderr.decode(encoding='UTF-8')
            warning_dialog = builder.get_object('warning_dialog')
            warning_dialog.set_markup("<b>Warning</b>")
            warning_dialog.format_secondary_markup(stderr)
            warning_dialog.show()
            return 1
        else:
            stdout = cp.stdout.decode(encoding='UTF-8')
        """

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
    pdb.set_trace()
    terminal = builder.get_object('terminal')
    buff = builder.get_object('terminal_buff')
    prj_cwd = project.working_directory
    thread = threading.Thread(target=execute_cmd, args=(cmds, terminal, buff, prj_cwd))
    thread.daemon = True
    thread.start()



        
                
