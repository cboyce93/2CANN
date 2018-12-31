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
    command.str = ""
    func_offset = len(command.func)
    flag_offsets = []
    static_offsets = []
    iter_offsets = []
    
    # reset active index
    #tagtable.foreach(reset_tags, None)
      
    #pdb.set_trace()
    buff = Gtk.TextBuffer.new(tagtable)
    command.str += command.func    
    
    # calculate offsets and build command string
    if len(command.flags) > 0:
        flag_offsets.append(func_offset + 1)
        for flag in command.flags:
            command.str += " " + flag
            offset = len(command.str)+1
            flag_offsets.append(offset)
        static_offsets.append(offset)
        for static in command.statics:
            command.str += " " + static[0] + " " + static[1]
            offset = len(command.str)+1
            static_offsets.append(offset)
        iter_offsets.append(offset)
        for iterr in command.iters:
            command.str += " " + iterr[0] + " " + iterr[1]
            offset = len(command.str)+1
            iter_offsets.append(offset)
    
    buff.set_text(command.str, -1)
    
    # apply tags
    
    # function tag
    if index == 0:
        buff.apply_tag_by_name("active_func", buff.get_start_iter(), buff.get_iter_at_offset(len(command.func)))
    else:
        buff.apply_tag_by_name("func", buff.get_start_iter(), buff.get_iter_at_offset(len(command.func)))
    
    # flag tag
    if len(flag_offsets) > 1:
        #pdb.set_trace()
        # drop last offset in loop since referenced by previous iteration
        for i, offset in enumerate(flag_offsets[:-1]):
            if index == i+1:
                buff.apply_tag_by_name("active_flag", buff.get_iter_at_offset(offset), buff.get_iter_at_offset(flag_offsets[i+1]))
            else:
                buff.apply_tag_by_name("flag", buff.get_iter_at_offset(offset), buff.get_iter_at_offset(flag_offsets[i+1]))
                
    # static tag
    if len(static_offsets) > 1:
        #pdb.set_trace()
        # drop last offset in loop since referenced by previous iteration
        for i, offset in enumerate(static_offsets[:-1]):
            if index == i+1+len(command.flags):
                buff.apply_tag_by_name("active_static", buff.get_iter_at_offset(offset), buff.get_iter_at_offset(static_offsets[i+1]))
            else:
                buff.apply_tag_by_name("static", buff.get_iter_at_offset(offset), buff.get_iter_at_offset(static_offsets[i+1]))
                
    # iter tag
    if len(iter_offsets) > 1:
        #pdb.set_trace()
        # drop last offset in loop since referenced by previous iteration
        for i, offset in enumerate(iter_offsets[:-1]):
            if index == i+1+len(command.iters)+len(command.statics):
                buff.apply_tag_by_name("active_itertag", buff.get_iter_at_offset(offset), buff.get_iter_at_offset(iter_offsets[i+1]))
            else:
                buff.apply_tag_by_name("itertag", buff.get_iter_at_offset(offset), buff.get_iter_at_offset(iter_offsets[i+1]))
       
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
    static.props.underline = 0
    static.props.underline_set = True
    
    # active static tag
    active_static = Gtk.TextTag.new("active_static")
    active_static.props.weight = 700
    active_static.props.scale = 1.3
    active_static.props.weight_set = True
    active_static.props.foreground = "green"
    active_static.props.underline = 1
    active_static.props.underline_set = True
    
    # iter tag
    itertag = Gtk.TextTag.new("itertag")
    itertag.props.weight = 500
    itertag.props.scale = 1.3
    itertag.props.weight_set = True
    itertag.props.foreground = "blue"
    itertag.props.underline = 0
    itertag.props.underline_set = True
    
    # active iter tag
    active_itertag = Gtk.TextTag.new("active_itertag")
    active_itertag.props.weight = 700
    active_itertag.props.scale = 1.3
    active_itertag.props.weight_set = True
    active_itertag.props.foreground = "blue"
    active_itertag.props.underline = 1
    active_itertag.props.underline_set = True   
    
    tagtable.add(func)
    tagtable.add(active_func)
    tagtable.add(flag)
    tagtable.add(active_flag)
    tagtable.add(static)
    tagtable.add(active_static)
    tagtable.add(itertag)
    tagtable.add(active_itertag)
    return tagtable

