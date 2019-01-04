#!/usr/bin/env python

""" This file contains subs related to file selection. Calls will be
    from the static/iter option editor windows
    """

import pdb

def parse_file_selection(file_selection, variables):
    #pdb.set_trace()
    for var in variables:
        file_selection = file_selection.replace(var[0], var[1])
    return file_selection
