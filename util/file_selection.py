#!/usr/bin/env python3

""" This file contains subs related to file selection. Calls will be
    from the static/iter option editor windows
    """
import subprocess as SP
from copy import deepcopy
import re
import pdb

def list_file_selection_contents(builder, project_vars, fs, ftype):
    fs, fs_arr, match = parse_file_selection(fs, project_vars)
    cmd = "ls -1"
    if not ftype:
        # add directory flag for directory type selections
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
            # iter through shell output of files which already exist
            # and add user prefix
            for fp in stdout.split("\n"):
                concat_fs.append(concatenate(fp, fs_arr))
            # print to buffer
            stdout = print_buffer(concat_fs)
        builder.get_object('file_selection_buffer').set_text(stdout, -1)   
        builder.get_object('file_selection_viewer').show()

def parse_file_selection(file_selection, variables):
    # find prefixes
    # find prefix with <> enclosure
    match = re.findall(r'(\<.*?\>)', file_selection)
    # replace any project variable strings with associated value pair
    for var in variables:
        file_selection = file_selection.replace(var[0], var[1])
    # remove the prefix string from the file selection since files
    # do not yet exist
    fs_arr = []
    if len(match) > 0:
        match = match[0]
        fs_arr = list(file_selection.partition(match))
        file_selection = file_selection.replace(match, "")       
    return (file_selection, fs_arr, match)

def concatenate(fp, fs_arr):
    """ Return concatenated string """
    arr = deepcopy(fs_arr)
    arr = remove_wildcards(fp, arr)
    to_concat = []
    for i,fs in enumerate(arr):
        if i == 2:
            return  "".join(str(y) for y in to_concat)
        if i % 2 != 0:
            tup = fp.partition(arr[i-1])
            to_concat.append(tup[1])
            to_concat.append(tup[2])
            to_concat.insert(i, fs[1:-1])

def remove_wildcards(fp, fs_arr):
    # find the all * chars and prepend with . and append ?
    # so we get .*? which can be used in regex to populate with
    # contents outputted by the shell
    # dont care about prefix so skip it
    for j in [0,2]:
        regex = fs_arr[j]
        no_of_wc = 0
        for i, char in enumerate(fs_arr[j]):
            if char == "*":
                regex = regex[:i+2*no_of_wc] + ".*?" + regex[i+2*no_of_wc+1:]
                no_of_wc += 1
        fs_arr[j] = regex
    m = re.findall(fs_arr[0], fp)
    fs_arr[0] = m[0]
    filename = fp.replace(fs_arr[0],"")
    fs_arr[2] = filename
    return fs_arr

def print_buffer(arr):
    x = ""
    for y in arr:
        x += y +"\n"
    return x  
