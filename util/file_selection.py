#!/usr/bin/env python

""" This file contains subs related to file selection. Calls will be
    from the static/iter option editor windows
    """
import subprocess as SP
import re
import pdb

def list_file_selection_contents(builder, project_vars, fs, ftype):
    fs, fs_arr, match = parse_file_selection(fs, project_vars)
    cmd = "ls -1"
    if not ftype:
        # add directory flag
        cmd += "d"
    cmd += " " + fs
    cp = SP.run([cmd], stdout=SP.PIPE, stderr=SP.PIPE, shell=True)
    if cp.returncode != 0:
        stderr = cp.stderr.decode(encoding='UTF-8')
        warning_dialog = builder.get_object('warning_dialog')
        warning_dialog.set_markup("<b>Warning</b>")
        warning_dialog.format_secondary_markup(stderr)
        warning_dialog.show()
    else:
        stdout = cp.stdout.decode(encoding='UTF-8')
        stdout = stdout.split("\n\n", 1)[0]
        # check for concatenations in entry
        if len(match) > 0:
            # collect newly concatenated selection in list
            concat_fs = []
            pdb.set_trace()
            for fp in stdout.split("\n"):
                concat_fs.append(concatenate(fp, fs_arr))
            
            stdout = print_buffer(concat_fs)
                        
        builder.get_object('file_selection_buffer').set_text(stdout, -1)   
        builder.get_object('file_selection_viewer').show()

def parse_file_selection(file_selection, variables):
    # find concatenations
    #match = re.findall(r'\<(.*?)\>', file_selection)
    # find concatenations with <> enclosures
    match = re.findall(r'(\<.*?\>)', file_selection)
    
    # replace any project variable strings with associated value pair
    for var in variables:
        file_selection = file_selection.replace(var[0], var[1])
    # remove the concatenation string from the file selection since files
    # do not yet exist
    fs_arr = []
    fs = file_selection
    if len(match) > 0:
        for i,m in enumerate(match):
            if i > 0:
                fs = list(fs_arr[3*i-1].partition(m))
                fs_arr.remove(fs_arr[-1])
                fs_arr = fs_arr + list(fs)
            else:
                fs_arr = list(file_selection.partition(m))
            file_selection = file_selection.replace(m, "")       
    return (file_selection, fs_arr, match)

def concatenate(fp, fs_arr):
    to_concat = []
    for i,fs in enumerate(fs_arr):
        if i == len(fs_arr)-1:
            return  "".join(str(y) for y in to_concat)
        if i % 2 != 0:
            tup = fp.partition(fs_arr[i-1])
            if tup[2] != '':
                to_concat.append(tup[1])
                to_concat.append(tup[2])
            to_concat.insert(i, fs[1:-1])
            fp = to_concat[i+1]

def print_buffer(arr):
    x = ""
    for y in arr:
        x += y +"\n"
    return x  
