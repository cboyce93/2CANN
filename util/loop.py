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

def view_loop(builder, project, liststore, local_var, dir_selection):
    pdb.set_trace()
    # split by directory level
    # replace global variables with user values
    dir_exp = dir_selection
    for var in project.vars:
        dir_exp = dir_exp.replace(var[0], var[1])
    # grab var tagged (<v>exp</v>) regex expression  
    m = re.search(r'(<v>%{.*?}</v>)', dir_exp)
    match = m[0]
    # remove identifier tags
    local_var_regex = match[5:-5]
    # populate with wildcard so we can regex match later
    dir_exp = dir_exp.replace("<v>%{" + local_var_regex + "}</v>" ,"*")
    # find all remaining regexes not flagged
    matches = re.findall(r'(%{.*?})', dir_exp)
    oth_regexes = []
    for m in matches:
        # replace regex with wildcard so we can match later
        dir_exp = dir_exp.replace(m, "*")
        oth_regexes.append(m[2:-1])
    # run subprocess
    cmd = "ls -1d " + dir_exp + "/"
    # cwd --> shell working directroy as specified in project preferences
    cp = SP.run([cmd], stdout=SP.PIPE, stderr=SP.PIPE, shell=True, cwd=project.working_directory)
    if cp.returncode != 0:
        stderr = cp.stderr.decode(encoding='UTF-8')
        warning_dialog = builder.get_object('warning_dialog')
        warning_dialog.set_markup("<b>Warning</b>")
        warning_dialog.format_secondary_markup(stderr)
        warning_dialog.show()
    else:
        stdout = cp.stdout.decode(encoding='UTF-8')
        # grab relevant output
        stdout = stdout.split("\n\n", 1)[0]
        #regex_str = ".*?"
        #for regex in oth_regex:
        #    regex_str += regex + ".*?"
        #m = re.findall(regex_str, stdout)
        stdout = stdout.split("\n")
        to_print = []
        liststore.clear()
        for line in stdout:
            # remove the terminating forward slash that we added to get ls
            # function to output only directories
            line = line[:-1]
            m = re.search(local_var_regex, line)
            if m is not None:
                liststore.append([m[0], line])
        return
"""
self.module.command.loops.append([loop_no,
                                    var,
                                    get_local_var_value(dir_selection),
                                    dir_selection])
                                    """
def view_looper(builder, project, loops):
    treeview = builder.get_object('loop_viewer_treeview')
    for col in treeview.get_columns():
        treeview.remove_column(col)
    
    column_titles = []
    dir_exp = ""
    for loop in loops:
        column_titles.append(loop[1])
        dir_exp += loop[3]
    column_titles.append("Directory Selection")
    
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
    
    
    
    



       

            
    
    
    
    
    
