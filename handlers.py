#!/usr/bin/env python3

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from lib.module import Module
from lib.command import Command
from lib.variable import Variable
from util.treeview import *
from util.validation import *
from util.command_editor import *
from util.file_selection import *
from util.loop import *
from util.run import *
from lib.load import load_module

# activate debugger
import pdb

class Handler:

    ###################################
    """ Global Handlers """
    ###################################
    
    def exit(self, wrapper, data=None):
        wrapper.destroy()
        Gtk.main_quit()
    
    def close(self, window, data=None):
        window.hide()
        # let GTK know the event has been handled and that it should
        # not perform the default action
        return True
    
    def close_button(self, window):
        window.hide()
        # let GTK know the event has been handled and that it should
        # not perform the default action
        return True
    
    def close_dialog(self, dialog, data=None):
        dialog.hide()
        return True
        
    ###################################
    """ Main Window Handlers """
    ###################################
            
    """ File Menu Handlers """
    
    """ Tools Menu Handlers """
    
    def on_variable_manager_activated(self, variable_manager):
        variable_manager.show()
    
    def on_preferences_manager_activated(self, preferences_manager):
        preferences_manager.show()
    
    """ Help Menu Handlers """
    
    def on_about_activated(self, about_dialog):
        about_dialog.show()
        
    """ Pipeline Editor Toolbar Handlers """
    
    ########################################
    """ Library Manager Handlers """
    ########################################
    
    def on_new_module_clicked(self, module_editor):
        self.builder.get_object('module_editor_header').set_title('New Module')
        # clear the entries
        self.builder.get_object('module_category_search_entry').set_text("")
        self.builder.get_object('module_name_entry').set_text("")
        self.builder.get_object('module_author_entry').set_text("")
        self.builder.get_object('module_description_entry').set_text("")
        self.builder.get_object('module_url_entry').set_text("")
        self.builder.get_object('module_command_entry').set_text("")
        # Create new Module object
        self.module = Module()
        module_editor.show()
    
    def on_editor_module_clicked(self, module_editor):
        self.builder.get_object('module_editor_header').set_title('Edit Module')
        self.builder.get_object('module_category_search_entry').set_text(self.module.category)
        self.builder.get_object('module_name_entry').set_text(self.module.name)
        self.builder.get_object('module_author_entry').set_text(self.module.author)
        self.builder.get_object('module_description_entry').set_text(self.module.desc)
        self.builder.get_object('module_url_entry').set_text(self.module.url)
        self.builder.get_object('module_command_entry').set_text("")
        module_editor.show()
    
    def on_lib_manager_selection_changed(self, selection):
        #pdb.set_trace()
        model, iterr = selection.get_selected()
        fp = model.get_value(iterr, 4)
        self.module = load_module(fp)
        
        
    ###################################
    """ Variable Manager Handlers"""
    ###################################
        
    def on_new_variable_clicked(self, variable_editor):
        self.variable = Variable()
        self.ve_state = 0
        self.builder.get_object('ve_header').set_title('New Variable')
        self.builder.get_object('ve_name_entry').set_text("")
        self.builder.get_object('ve_file_selection_entry').set_text("")
        
        variable_editor.show()
        
    def on_edit_variable_clicked(self, variable_editor):
        self.builder.get_object('ve_header').set_title('Edit Variable')
        self.ve_state = 1
        model, self.treeiter = self.builder.get_object('vm_treeview_selection').get_selected()
        if self.treeiter is not None:
            self.builder.get_object('ve_name_entry').set_text(model[self.treeiter][0][2:-1])
            self.builder.get_object('ve_file_selection_entry').set_text(model[self.treeiter][1])
            variable_editor.show()
    
    def on_del_variable_clicked(self, variable_editor):
        model, self.treeiter = self.builder.get_object('vm_treeview_selection').get_selected()
        self.variables_liststore.remove(self.treeiter)
    
    def on_vm_ok_button_clicked(self, variable_manager):
        serialize_treemodel(self.builder.get_object('vm_treeview').get_model(),
                            self.project)
        self.builder.get_object('variable_editor').hide()
        variable_manager.hide()

    ###################################
    """ Preferences Handlers"""
    ###################################
    
    def on_work_dir_chooser_file_set(self, file_chooser):
        self.project.working_directory = file_chooser.get_filename()   
    
    ###################################
    """ Variable Editor Handlers"""
    ###################################    
    
    def on_ve_ok_button_clicked(self, variable_editor):
        name = self.builder.get_object('ve_name_entry').get_text()
        fs = self.builder.get_object('ve_file_selection_entry').get_text()
        # CALL VALIDATION SUB HERE
        self.variable.name = "${" + name +"}"
        self.variable.val = fs
        if self.ve_state == 0:
            self.variables_liststore.append([self.variable.name, self.variable.val])
        else:
            self.variables_liststore.set_value(self.treeiter, 0 , self.variable.name)
            self.variables_liststore.set_value(self.treeiter, 1, self.variable.val)                       
        variable_editor.hide() 
    
    ###################################
    """ Module Editor Handlers"""
    ###################################
    
    def on_cmd_editor_clicked(self, command_editor):
        update_textview(self.builder.get_object('command_editor_textview'),
                                                self.module.command,
                                                self.tagtable,
                                                get_spinner_index(self.builder.get_object('index_spin_button')))
        command_editor.show()
        
    def on_save_module_button_clicked(self, data=None):
        self.module.category = self.builder.get_object('module_category_search_entry').get_text()
        self.module.name = self.builder.get_object('module_name_entry').get_text()
        self.module.author = self.builder.get_object('module_author_entry').get_text()
        self.module.desc = self.builder.get_object('module_description_entry').get_text()
        self.module.url = self.builder.get_object('module_url_entry').get_text()
        #### need to add this after self.module.command = None 
        # validate
        valid, error_message = validate_module(self.module)
        if valid:
            self.module.save(self.project.root)
            info_dialog = self.builder.get_object('info_dialog')
            info_dialog.set_markup("<b>Info</b>")
            info_dialog.format_secondary_markup(self.module.name + ".mod saved successfully.")
            info_dialog.show()
            self.lib_liststore.append([self.module.category, 
                                        self.module.name,
                                        self.module.author,
                                        self.module.desc,
                                        self.module.fp])
            self.builder.get_object('module_editor').hide()     
        else:
            warning_dialog = self.builder.get_object('warning_dialog')
            warning_dialog.set_markup("<b>Warning</b>")
            warning_dialog.format_secondary_markup(error_message)
            warning_dialog.show()
            
    def on_module_editor_focus_in_event(self, module_command_entry, widget):
        if self.module.command is not None:
            module_command_entry.set_text(self.module.command.str)
            
    ##############################
    """ Command Editor Handlers"""
    ##############################   
    
    def on_index_spin_button_value_changed(self, index_spin_button):
        update_textview(self.builder.get_object('command_editor_textview'), 
                                                self.module.command,
                                                self.tagtable,
                                                get_spinner_index(self.builder.get_object('index_spin_button')))       

    
    def ce_on_add_loop_clicked(self, loop_editor):
        self.builder.get_object('le_var_entry').set_text("")
        self.builder.get_object('le_dir_selection_entry').set_text("")
        loop_editor.show()
    
    def ce_on_view_loop_clicked(self, loop_viewer):
        view_looper(self.builder, self.project, self.module.command.loops)
        loop_viewer.show()
    
    def ce_on_run_clicked(self, data=None):
        pdb.set_trace()
        run_module(self.builder, self.project, self.module)
    
    def on_add_function_clicked(self, function_editor):
        if self.module.command.func[2] is "":
            function_editor.show()
        else:
            self.builder.get_object('function_editor_header').set_title('Edit Function')
            self.builder.get_object('function_editor_entry').set_text(self.module.command.func[2])
            function_editor.show()
    
    def on_add_flag_option_clicked(self, flag_option_editor):
        self.edit_flag = False, None
        self.builder.get_object('foe_header').set_title("Add Flag Option")
        self.builder.get_object('foe_flag_entry').set_text("")
        flag_option_editor.show()
        
    def on_add_static_option_clicked(self, static_option_editor):
        self.edit_flag = False, None
        self.builder.get_object('soe_header').set_title("Add Static Option")
        self.builder.get_object('soe_flag_entry').set_text("")
        self.builder.get_object('soe_static_arg_entry').set_text("")
        static_option_editor.show()
    
    def on_add_set_option_clicked(self, set_option_editor):
        self.edit_flag = False, None
        self.builder.get_object('se_header').set_title("Add Set Option")
        self.builder.get_object('se_flag_entry').set_text("")
        self.builder.get_object('se_radio_file').set_active(True)
        self.builder.get_object('se_file_selection_entry').set_text("")
        self.builder.get_object('se_radio_none').set_active(True)
        self.builder.get_object('se_match_none').set_active(True)
        set_option_editor.show()
        
    def on_ce_edit_button_clicked(self, data=None):
        index = get_spinner_index(self.builder.get_object('index_spin_button'))
        if index == self.module.command.func[0]:
            # Edit function
            self.builder.get_object('function_editor_header').set_title('Edit Function')
            self.builder.get_object('function_editor_entry').set_text(self.module.command.func[2])
            self.builder.get_object('function_editor').show()
            return
        for i,flag in enumerate(self.module.command.flags):
            if index == flag[0]:
                self.edit_flag = True, i
                self.builder.get_object('foe_header').set_title("Edit Flag Option")
                self.builder.get_object('foe_flag_entry').set_text(flag[2])
                self.builder.get_object('flag_option_editor').show()
                return
        for i,static in enumerate(self.module.command.statics):
            if index == static[0]:
                self.edit_flag = True, i
                self.builder.get_object('soe_header').set_title("Edit Static Option")
                self.builder.get_object('soe_flag_entry').set_text(static[2])
                self.builder.get_object('soe_static_arg_entry').set_text(static[3])
                self.builder.get_object('static_option_editor').show()
                return
        for i,sett in enumerate(self.module.command.sets):
            if index == sett[0]:
                self.edit_flag = True, i
                self.builder.get_object('se_header').set_title("Edit Set Option")
                self.builder.get_object('se_flag_entry').set_text(sett[2])
                if sett[3] == "file":
                    self.builder.get_object('se_radio_file').set_active(True)
                else:
                    self.builder.get_object('se_radio_directory').set_active(True)   
                self.builder.get_object('se_file_selection_entry').set_text(sett[4])
                if sett[5] == "none":
                    self.builder.get_object('se_radio_none').set_active(True)
                elif sett[5] == "input":
                    self.builder.get_object('se_radio_input').set_active(True)
                else:
                    self.builder.get_object('se_radio_output').set_active(True)
                if sett[6] == 'none':
                    self.builder.get_object('se_match_none').set_active(True)
                elif sett[6] == 'source':
                    self.builder.get_object('se_match_source').set_active(True)
                else:
                    self.builder.get_object('se_match_clone').set_active(True)
                self.builder.get_object('set_option_editor').show()
                return
    
    def on_ce_del_button_clicked(self, data=None):
        #pdb.set_trace()
        index = get_spinner_index(self.builder.get_object('index_spin_button'))
        if index == self.module.command.func[0]:
            self.module.command.func = [None, None, ""]
        for i,flag in enumerate(self.module.command.flags):
            if index == flag[0]:
                self.module.command.flags.remove(flag)
        for i,static in enumerate(self.module.command.statics):
            if index == static[0]:
                self.module.command.statics.remove(static)
        for i,sett in enumerate(self.module.command.sets):
            if index == sett[0]:
                self.module.command.sets.remove(sett)
        update_textview(self.builder.get_object('command_editor_textview'), 
                                                self.module.command,
                                                self.tagtable,
                                                get_spinner_index(self.builder.get_object('index_spin_button')))
            
    def on_command_editor_delete_event(self, command_editor, data=None):
        buff = Gtk.TextBuffer.new()
        buff.set_text("", -1)
        self.builder.get_object('command_editor_textview').set_buffer(buff)
        self.builder.get_object('index_spin_button').set_value(float(0))
        command_editor.hide()
        return True
    
    
    ###################################
    """ Loop Editor Handlers"""
    ###################################
    
    def on_view_loop_clicked(self, loop_viewer):
        local_var = self.builder.get_object('le_var_entry').get_text()
        dir_selection = self.builder.get_object('le_dir_selection_entry').get_text()
        view_loop(self.builder, self.project, self.lv_liststore, local_var, dir_selection)
        loop_viewer.show()
    
    def on_le_ok_button_clicked(self, loop_editor):
        var = self.builder.get_object('le_var_entry').get_text()
        dir_selection = self.builder.get_object('le_dir_selection_entry').get_text()
        loop_no = len(self.module.command.loops)+1
        self.module.command.loops.append([loop_no,
                                    "$"+var,
                                    get_local_var_value(dir_selection),
                                    dir_selection])
        self.loop_liststore.append([loop_no,
                                    "$"+var,
                                    get_local_var_value(dir_selection),
                                    dir_selection])
        loop_editor.hide()
    
    ###################################
    """ Function Editor Handlers"""
    ###################################
    
    def on_fe_ok_button_clicked(self, function_editor):
        # !! NOTE need to do validation here
        self.module.command.func = [None, "func", self.builder.get_object('function_editor_entry').get_text()]
        self.builder.get_object('adjustment').set_upper(self.module.command.get_max_index())
        update_textview(self.builder.get_object('command_editor_textview'),
                                                self.module.command,
                                                self.tagtable,
                                                get_spinner_index(self.builder.get_object('index_spin_button')))
        function_editor.hide()
        
    ###################################
    """ Flag Option Editor Handlers"""
    ###################################
    
    def on_foe_ok_button_clicked(self, flag_option_editor):
        # !! NOTE need to do validation here
        flag = self.builder.get_object('foe_flag_entry').get_text()
        edit, index = self.edit_flag
        if not edit:
            self.module.command.flags.append([None, "flag", flag])
        else:
            self.module.command.flags[index][2] = flag
        self.builder.get_object('adjustment').set_upper(self.module.command.get_max_index())
        update_textview(self.builder.get_object('command_editor_textview'), self.module.command, self.tagtable, get_spinner_index(self.builder.get_object('index_spin_button')))
        flag_option_editor.hide()
        
    ####################################
    """ Static Option Editor Handlers"""
    ####################################
    
    def on_soe_ok_button_clicked(self, static_option_editor):
        flag = self.builder.get_object('soe_flag_entry').get_text()
        static_arg = self.builder.get_object('soe_static_arg_entry').get_text()
        
        edit, index = self.edit_flag
        if not edit:
            self.module.command.statics.append([None, 
                                                "static", 
                                                flag,
                                                static_arg])
        else:
            self.module.command.statics[index][2] = flag
            self.module.command.statics[index][3] = static_arg
        
        self.builder.get_object('adjustment').set_upper(self.module.command.get_max_index())
        update_textview(self.builder.get_object('command_editor_textview'), 
                                                self.module.command,
                                                self.tagtable,
                                                get_spinner_index(self.builder.get_object('index_spin_button')))
        static_option_editor.hide()

    ####################################
    """ Set Option Editor Handlers"""
    ####################################
    
    def on_se_ok_button_clicked(self, set_option_editor):
        flag = self.builder.get_object('se_flag_entry').get_text()
        file_type_selection = self.builder.get_object('se_radio_file').get_active()
        file_selection = self.builder.get_object('se_file_selection_entry').get_text()
        none_tag_selection = self.builder.get_object('se_radio_none').get_active()
        input_tag_selection = self.builder.get_object('se_radio_input').get_active()
        none_match_selection = self.builder.get_object('se_match_none').get_active()
        source_match_selection = self.builder.get_object('se_match_source').get_active()
        # !! NOTE need to do validation here 
        if file_type_selection:
            file_selection_type = "file"
        else:
            file_selection_type = "directory"
        
        if none_tag_selection:
            file_selection_tag = 'none'
        elif input_tag_selection:
            file_selection_tag = 'input'
        else:
            file_selection_tag = 'output'
        
        if none_match_selection:
            matching = 'none'
        elif source_match_selection:
            matching = 'source'
        else:
            matching = 'clone'
        
        edit, index = self.edit_flag
        if not edit:
            self.module.command.sets.append([None,
                                            "iter",
                                            flag,
                                            file_selection_type,
                                            file_selection,
                                            file_selection_tag,
                                            matching])
        else:
            self.module.command.sets[index][2] = flag
            self.module.command.sets[index][3] = file_selection_type
            self.module.command.sets[index][4] = file_selection
            self.module.command.sets[index][5] = file_selection_tag
            self.module.command.sets[index][6] = matching
            
        
        self.builder.get_object('adjustment').set_upper(self.module.command.get_max_index())
        update_textview(self.builder.get_object('command_editor_textview'), 
                                                self.module.command,
                                                self.tagtable,
                                                get_spinner_index(self.builder.get_object('index_spin_button')))
        set_option_editor.hide()
        
    def on_ioe_view_selection_button_clicked(self, file_selection_viewer):
        # get file selection & file type from entry
        ftype = self.builder.get_object('se_radio_file').get_active()
        if not ftype:
            ftype = False      
        fs = self.builder.get_object('se_file_selection_entry').get_text()
        # CALL VALIDATION SUB HERE
        # !!! NOTE for file type selections, last char must not be /
        # !!! NOTE for directory type selections, last character must not be
        # wildcard *
        list_file_selection_contents(self.builder, self.project.vars, fs, ftype)
    
    ######################################
    """ File Selection Viewer Handlers"""
    ######################################
    
    #handlers go here
    
    ######################################
    
    def __init__(self, project, builder, liststores, tagtable):
        self.project = project
        self.builder = builder
        self.variables_liststore = liststores[0]
        self.lib_liststore = liststores[1]
        self.loop_liststore = liststores[2]
        self.lv_liststore = liststores[3]
        self.tagtable = tagtable
        self.module = None
        self.variable = None
        self.stdout = ""      
    

