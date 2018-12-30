#!/usr/bin/env python

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import pdb

""" 
Command Editor Subs

This file contains all the subs for the command_editor window that we
want to keep out of the handlers.py file
    
"""

def update_textview(textview, command):
    tagtable = init_tagtable()
    
    # init vars
    cmd_str = ""
    func_offset = len(command.func)
    flag_offset = None
    static_offset = None
    iter_offset = None
    #pdb.set_trace()
    buff = Gtk.TextBuffer.new(tagtable)
    cmd_str += command.func    
    
    if len(command.flags) > 0:
        flag_offset = 0
        for flag in command.flags:
            flag_offset += len(flag)
            cmd_str += " " + flag
        flag_offset += func_offset + len(command.flags)
    
    buff.set_text(cmd_str, -1)
    # apply tags
    buff.apply_tag_by_name("func", buff.get_start_iter(), buff.get_iter_at_offset(len(command.func)))
    if flag_offset is not None:
        buff.apply_tag_by_name("flag", buff.get_iter_at_offset(len(command.func)), buff.get_iter_at_offset(flag_offset))
    #buff.apply_tag_by_name("static", buff.get_iter_at_offset(10), buff.get_iter_at_offset(23))
    #buff.apply_tag_by_name("iter", buff.get_iter_at_offset(24), buff.get_end_iter())
    
    textview.set_buffer(buff)
    
def init_tagtable():
    
    tagtable = Gtk.TextTagTable.new()
    # func tag
    func = Gtk.TextTag.new("func")
    func.props.weight = 700
    func.props.scale = 1.3
    func.props.weight_set = True
    func.props.foreground = "black"

    # flag tag
    flag = Gtk.TextTag.new("flag")
    flag.props.weight = 500
    flag.props.scale = 1.3
    flag.props.weight_set = True
    flag.props.foreground = "brown"
    
    # static tag
    static = Gtk.TextTag.new("static")
    static.props.weight = 500
    static.props.scale = 1.3
    static.props.weight_set = True
    static.props.foreground = "green" 
    
    # iter tag
    itertag = Gtk.TextTag.new("iter")
    itertag.props.weight = 500
    itertag.props.scale = 1.3
    itertag.props.weight_set = True
    itertag.props.foreground = "blue"
    
    tagtable.add(func)
    tagtable.add(flag)
    tagtable.add(static)
    tagtable.add(itertag)
    return tagtable

