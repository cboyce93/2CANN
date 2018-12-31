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

def update_textview(textview, command, tagtable, index):
    
    # init vars
    cmd_str = ""
    func_offset = len(command.func)
    flag_offsets = []
    static_offsets = []
    iter_offsets = []
    
    # reset active index
    #tagtable.foreach(reset_tags, None)
      
    #pdb.set_trace()
    buff = Gtk.TextBuffer.new(tagtable)
    cmd_str += command.func    
    
    if len(command.flags) > 0:
        offset = func_offset
        for flag in command.flags:
            cmd_str += " " + flag
            offset += len(flag) + 1
            flag_offsets.append(offset)
    
    buff.set_text(cmd_str, -1)
    
    # apply tags
    if index == 0:
        buff.apply_tag_by_name("active_func", buff.get_start_iter(), buff.get_iter_at_offset(len(command.func)))
    else:
        buff.apply_tag_by_name("func", buff.get_start_iter(), buff.get_iter_at_offset(len(command.func)))
    if len(flag_offsets) > 0:
        for i, offset in enumerate(flag_offsets):
            if i == 0 and index == 1:
                buff.apply_tag_by_name("active_flag", buff.get_iter_at_offset(func_offset + 1), buff.get_iter_at_offset(offset))
            elif i == 0:
                buff.apply_tag_by_name("flag", buff.get_iter_at_offset(func_offset + 1), buff.get_iter_at_offset(offset))
            elif i+1 == index:
                buff.apply_tag_by_name("active_flag", buff.get_iter_at_offset(flag_offsets[i - 1] + 1), buff.get_iter_at_offset(offset)) 
            else:
                buff.apply_tag_by_name("flag", buff.get_iter_at_offset(flag_offsets[i - 1] + 1), buff.get_iter_at_offset(offset))    
        
    #buff.apply_tag_by_name("static", buff.get_iter_at_offset(10), buff.get_iter_at_offset(23))
    #buff.apply_tag_by_name("iter", buff.get_iter_at_offset(24), buff.get_end_iter())
    
    textview.set_buffer(buff)
    
def init_tagtable():
    tagtable = Gtk.TextTagTable.new()
    # func tag
    func = Gtk.TextTag.new("func")
    func.props.weight = 500
    func.props.scale = 1.3
    func.props.weight_set = True
    func.props.foreground = "black"
    func.props.underline = 0
    func.props.underline_set = True
    
    # func tag
    active_func = Gtk.TextTag.new("active_func")
    active_func.props.weight = 700
    active_func.props.scale = 1.3
    active_func.props.weight_set = True
    active_func.props.foreground = "black"
    active_func.props.underline = 1
    active_func.props.underline_set = True

    # flag tag
    flag = Gtk.TextTag.new("flag")
    flag.props.weight = 500
    flag.props.scale = 1.3
    flag.props.weight_set = True
    flag.props.foreground = "brown"
    flag.props.underline = 0
    flag.props.underline_set = True
    
    # active flag tag
    active_flag = Gtk.TextTag.new("active_flag")
    active_flag.props.weight = 700
    active_flag.props.scale = 1.3
    active_flag.props.weight_set = True
    active_flag.props.foreground = "brown"
    active_flag.props.underline = 1
    active_flag.props.underline_set = True
    
    # static tag
    static = Gtk.TextTag.new("static")
    static.props.weight = 500
    static.props.scale = 1.3
    static.props.weight_set = True
    static.props.foreground = "green"
    static.props.underline_set = True
    
    # iter tag
    itertag = Gtk.TextTag.new("iter")
    itertag.props.weight = 500
    itertag.props.scale = 1.3
    itertag.props.weight_set = True
    itertag.props.foreground = "blue"
    itertag.props.underline_set = True
    
    
    tagtable.add(func)
    tagtable.add(active_func)
    tagtable.add(flag)
    tagtable.add(active_flag)
    tagtable.add(static)
    tagtable.add(itertag)
    return tagtable

