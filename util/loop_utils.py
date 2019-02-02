#!/usr/bin/env python3

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import subprocess as SP
import re
import pdb
    
def get_local_var_value(dir_selection):
    """return value encased by var tags: <v>value</v>"""
    m = re.search(r'(\<v\>.*?\<\/v\>)', dir_selection)
    return m[0][3:-4]
    
def concat_dir_selections(loops):
    """concatenate dir selection of each loop
    i.e.,
    loop 1 directory selection: /${ROOT}/<v>%{(SUB..)}/</v>
    loop 2 directory selection: */<v>%{(RUN..)}</v>/
    
    output /${ROOT}/<v>%{(SUB..)}/*/<v>%{(RUN..)}</v>
    """
    concated_dir_selection = ""
    for loop in loops:
        concated_dir_selection += loop[3]
    return concated_dir_selection

def get_execution_filepath(full_path, project_vars, loops):
    """  
    Return path of the directory to prefix module command input files. This
    is not execution directory, since shell is always run from project working
    directory specified in preferences. It is relative directory from shell
    location.
    
    Also return array of local_var_regexes encased by <v></v> identifier tags
    and array of any other regexes specified.
    
    full path: concatenated loop dir selections
    """
    # replace global variables with user values
    for var in project_vars:
        full_path = full_path.replace(var[0], var[1])
    
    # grab var tagged (<v>exp</v>) regex expression  
    var_matches = re.findall(r'(<v>%{.*?}</v>)', full_path)
    # create a key-value dict to store tagged regex expressions
    local_var_regexes = {}
    for i,m in enumerate(var_matches):
        # populate with wildcard so we can regex match later
        full_path = full_path.replace(m ,"*")
        # remove identifier tags
        local_var_regexes[loops[i][1]] = m[5:-5]

    # find all remaining regexes not flagged
    reg_matches = re.findall(r'(%{.*?})', full_path)
    regexes = []
    for m in reg_matches:
        # replace regex with wildcard so we can match later
        full_path = full_path.replace(m, "*")
        regexes.append(m[2:-1])
    return (full_path, local_var_regexes, regexes)

def build_directory_set(builder, project, dir_exp, file_sel, local_var_regexes, regexes):
    # run subprocess
    cmd = "ls -1d " + dir_exp + "/"
    # cwd --> shell working directroy as specified in project preferences
    cp = SP.run([cmd], stdout=SP.PIPE, stderr=SP.PIPE, shell=True, cwd=project.working_directory)
    if cp.returncode != 0:
        # pop up warning dialog for non zero return code
        stderr = cp.stderr.decode(encoding='UTF-8')
        warning_dialog = builder.get_object('warning_dialog')
        warning_dialog.set_markup("<b>Warning</b>")
        warning_dialog.format_secondary_markup(stderr)
        warning_dialog.show()
    else:
        stdout = cp.stdout.decode(encoding='UTF-8')
        # grab relevant output
        stdout = stdout.split("\n\n", 1)[0]
        stdout = stdout.split("\n")
        dir_set = []
        # check if each of the regexes grab an output. This will validate
        # whether the line in the output is a selection we want or one 
        # that we want to discard
        for line in stdout:
            if line.isspace() or line == '':
                continue
            # all of the following must match otherwise line is discarded
            discard_line = False
            for i, key in enumerate(local_var_regexes):
                m = re.search(local_var_regexes[key], line)
                if m is None:
                    discard_line = True
            for regex in regexes:
                m = re.search(regex, line)
            if m is None:
               discard_line = True
            if not discard_line:
                dir_set.append(line)
        return dir_set

def view_loop_directories(builder, project, loops):
    treeview = builder.get_object('loop_viewer_treeview')
    # clear out columns from last build
    for col in treeview.get_columns():
        treeview.remove_column(col)
    
    column_titles = []
    dir_exp = ""
    # create columns for $var value
    for loop in loops:
        column_titles.append(loop[1])
        dir_exp += loop[3]
    column_titles.append("Directory Selection")
    
    # create liststore wiht extra spaces to allow for more loops
    lv_liststore = Gtk.ListStore(str, str, str, str, str, str, str, str)
    treeview.set_model(lv_liststore)
    
    for i, col_title in enumerate(column_titles):
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(col_title, renderer, text=i)
        column.set_sort_column_id(i)
        treeview.append_column(column)
    
    col_title="N/A"
    # make the extra columns invisible 
    for i in range(i+1, 8):
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(col_title, renderer, text=i)
        column.set_sort_column_id(i)
        treeview.append_column(column)
        column.set_visible(False)
        
    # replace global variables with user values
    for var in project.vars:
        dir_exp = dir_exp.replace(var[0], var[1])
    
    # grab var tagged (<v>exp</v>) regex expression  
    var_matches = re.findall(r'(<v>%{.*?}</v>)', dir_exp)
    # place to store regex expressions without user inputted tags
    local_var_regexes = []
    for m in var_matches:
        # populate with wildcard so we can regex match later
        dir_exp = dir_exp.replace(m ,"*")
        # remove identifier tags
        local_var_regexes.append(m[5:-5])

    # find all remaining regexes not flagged
    reg_matches = re.findall(r'(%{.*?})', dir_exp)
    regexes = []
    for m in reg_matches:
        # replace regex with wildcard so we can match later
        dir_exp = dir_exp.replace(m, "*")
        regexes.append(m[2:-1])
        
    # run subprocess
    cmd = "ls -1d " + dir_exp + "/"
    # cwd --> shell working directroy as specified in project preferences
    cp = SP.run([cmd], stdout=SP.PIPE, stderr=SP.PIPE, shell=True, cwd=project.working_directory)
    if cp.returncode != 0:
        # pop up warning dialog for non zero return code
        stderr = cp.stderr.decode(encoding='UTF-8')
        warning_dialog = builder.get_object('warning_dialog')
        warning_dialog.set_markup("<b>Warning</b>")
        warning_dialog.format_secondary_markup(stderr)
        warning_dialog.show()
    else:
        stdout = cp.stdout.decode(encoding='UTF-8')
        # grab relevant output
        stdout = stdout.split("\n\n", 1)[0]
        stdout = stdout.split("\n")
        to_print = []
        lv_liststore.clear()
        for line in stdout:
            if line.isspace() or line == '':
                continue
            # remove the terminating forward slash that we added to get ls
            # function to output only directories
            line = line[:-1]
            liststore_row = []
            for i, local_var_regex in enumerate(local_var_regexes):
                m = re.search(local_var_regex, line)
                if m is not None:
                    liststore_row.append(m[i])
            liststore_row.append(line)  
            # make line length equal to 8
            while len(liststore_row) < 8:
                liststore_row.append("N/A")
            lv_liststore.append(liststore_row)
        return
    
