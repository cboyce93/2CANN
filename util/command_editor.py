#!/usr/bin/env python3

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
  

def update_textview(textview, command, tagtable, spinner_index):
    """ Display command in textview following a change to command """
    # init vars
    command.str = ""
    flag_offsets = []
    static_offsets = []
    set_offsets = []
      
    buff = Gtk.TextBuffer.new(tagtable)
    
    # calculate offsets and build command string
    offset = 0
    index = 0
    
    if command.func[2] != "":
        command.str += command.func[2]
        command.func[0] = 0
        index += 1
        offset = len(command.str)
    if len(command.flags) > 0:
        flag_offsets.append(offset + 1)
        for flag in command.flags:
            command.str += " " + flag[2]
            flag[0] = index
            index += 1
            offset = len(command.str)+1
            flag_offsets.append(offset)
    if len(command.statics) > 0:
        static_offsets.append(offset)
        for static in command.statics:
            command.str += " " + static[2] + " " + static[3]
            static[0] = index
            index += 1
            offset = len(command.str)+1
            static_offsets.append(offset)
    if len(command.sets) > 0:
        set_offsets.append(offset)
        for iterr in command.sets:
            command.str += " " + iterr[2] + " " + iterr[4]
            iterr[0] = index
            index += 1
            offset = len(command.str)+1
            set_offsets.append(offset)
    
    buff.set_text(command.str, -1)
    
    # apply tags
    
    # function tag
    if command.func[2] != "":
        if spinner_index == get_func_index(command):
            buff.apply_tag_by_name("active_func", 
                                    buff.get_start_iter(), 
                                    buff.get_iter_at_offset(len(command.func[2])))
        else:
            buff.apply_tag_by_name("func", 
                                    buff.get_start_iter(), 
                                    buff.get_iter_at_offset(len(command.func[2])))
    
    # flag tag
    if len(flag_offsets) > 1:
        #pdb.set_trace()
        # drop last offset in loop since referenced by previous iteration
        for i, offset in enumerate(flag_offsets[:-1]):
            if spinner_index == get_flag_index(command, i):
                buff.apply_tag_by_name("active_flag", 
                                        buff.get_iter_at_offset(offset), 
                                        buff.get_iter_at_offset(flag_offsets[i+1]))
            else:
                buff.apply_tag_by_name("flag", 
                                        buff.get_iter_at_offset(offset), 
                                        buff.get_iter_at_offset(flag_offsets[i+1]))
                
    # static tag
    if len(static_offsets) > 1:
        #pdb.set_trace()
        # drop last offset in loop since referenced by previous iteration
        for i, offset in enumerate(static_offsets[:-1]):
            if spinner_index == get_static_index(command, i):
                buff.apply_tag_by_name("active_static", 
                                        buff.get_iter_at_offset(offset),
                                        buff.get_iter_at_offset(static_offsets[i+1]))
            else:
                buff.apply_tag_by_name("static",
                                        buff.get_iter_at_offset(offset), 
                                        buff.get_iter_at_offset(static_offsets[i+1]))
                
    # set tag
    if len(set_offsets) > 1:
        #pdb.set_trace()
        # drop last offset in loop since referenced by previous iteration
        for i, offset in enumerate(set_offsets[:-1]):
            if spinner_index == get_iter_index(command, i):
                buff.apply_tag_by_name("active_set_tag", 
                                        buff.get_iter_at_offset(offset),
                                        buff.get_iter_at_offset(set_offsets[i+1]))
            else:
                buff.apply_tag_by_name("set_tag", 
                                        buff.get_iter_at_offset(offset), 
                                        buff.get_iter_at_offset(set_offsets[i+1]))
       
    textview.set_buffer(buff)

def get_func_index(command):
    if command.func[2] == "":
        return -1
    else:
        return 0

def get_flag_index(command, index):
    if command.func[2] == "":
        return index
    else:
        return 1 + index

def get_static_index(command, index):
    if command.func[2] == "":
        return index + len(command.flags)
    else:
        return 1 + index + len(command.flags)

def get_iter_index(command, index):
    if command.func[2] == "":
        return index + len(command.flags) + len(command.statics)
    else:
        return 1 + index + len(command.flags) + len(command.statics)

def get_spinner_index(spinner):
        return spinner.get_value_as_int()

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
    
    # active set tag
    active_set_tag = Gtk.TextTag.new("active_set_tag")
    active_set_tag.props.weight = 700
    active_set_tag.props.scale = 1.3
    active_set_tag.props.weight_set = True
    active_set_tag.props.foreground = "blue"
    active_set_tag.props.underline = 1
    active_set_tag.props.underline_set = True
    
    # set tag
    set_tag = Gtk.TextTag.new("set_tag")
    set_tag.props.weight = 500
    set_tag.props.scale = 1.3
    set_tag.props.weight_set = True
    set_tag.props.foreground = "blue"
    set_tag.props.underline = 0
    set_tag.props.underline_set = True
    
    tagtable.add(func)
    tagtable.add(active_func)
    tagtable.add(flag)
    tagtable.add(active_flag)
    tagtable.add(static)
    tagtable.add(active_static)
    tagtable.add(set_tag)
    tagtable.add(active_set_tag)
    
    return tagtable

