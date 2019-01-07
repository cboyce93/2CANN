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
        print(self.module.command)
        self.module = load_module(fp)
        print(self.module.command)
        
        
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
            self.variables_liststore.set_value(self.treeiter, [self.variable.name, self.variable.val])
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
        print(self.module.command.str)
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
        flag_option_editor.show()
        
    def on_add_static_option_clicked(self, static_option_editor):
        self.edit_flag = False, None
        self.builder.get_object('soe_header').set_title("Add Static Option")
        static_option_editor.show()
    
    def on_add_iter_option_clicked(self, iter_option_editor):
        self.edit_flag = False, None
        self.builder.get_object('soe_header').set_title("Add Iterative Option")
        iter_option_editor.show()
        
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
                if static[3] == "file":
                    self.builder.get_object('soe_radio_file').set_active(True)
                else:
                    self.builder.get_object('soe_radio_directory').set_active(True)   
                self.builder.get_object('soe_file_selection_entry').set_text(static[4])
                if static[5] == "none":
                    self.builder.get_object('soe_radio_none').set_active(True)
                elif static[5] == "input":
                    self.builder.get_object('soe_radio_input').set_active(True)
                else:
                    self.builder.get_object('soe_radio_output').set_active(True)
                self.builder.get_object('common_root_dir_entry').set_text(static[6])
                self.builder.get_object('static_option_editor').show()
                return
        for i,iterr in enumerate(self.module.command.iters):
            if index == iterr[0]:
                self.edit_flag = True, i
                self.builder.get_object('soe_header').set_title("Edit Iterative Option")
                self.builder.get_object('ioe_flag_entry').set_text(iterr[2])
                if iterr[3] == "file":
                    self.builder.get_object('ioe_radio_file').set_active(True)
                else:
                    self.builder.get_object('ioe_radio_directory').set_active(True)   
                self.builder.get_object('ioe_file_selection_entry').set_text(iterr[4])
                if iterr[5] == "none":
                    self.builder.get_object('ioe_radio_none').set_active(True)
                elif iterr[5] == "input":
                    self.builder.get_object('ioe_radio_input').set_active(True)
                else:
                    self.builder.get_object('ioe_radio_output').set_active(True)
                self.builder.get_object('iter_option_editor').show()
                return
    
    def on_command_editor_delete_event(self, command_editor, data=None):
        buff = Gtk.TextBuffer.new()
        buff.set_text("", -1)
        self.builder.get_object('command_editor_textview').set_buffer(buff)
        self.builder.get_object('index_spin_button').set_value(float(0))
        command_editor.hide()
        return True
    
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
        file_type_selection = self.builder.get_object('soe_radio_file').get_active()
        file_selection = self.builder.get_object('soe_file_selection_entry').get_text()
        none_tag_selection = self.builder.get_object('soe_radio_none').get_active()
        input_tag_selection = self.builder.get_object('soe_radio_input').get_active()
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
            
        common_root = self.builder.get_object('common_root_dir_entry').get_text()
        
        edit, index = self.edit_flag
        if not edit:
            self.module.command.statics.append([None, 
                                                "static", 
                                                flag,
                                                file_selection_type,
                                                file_selection,
                                                file_selection_tag,
                                                common_root])
        else:
            self.module.command.statics[index][2] = flag
            self.module.command.statics[index][3] = file_selection_type
            self.module.command.statics[index][4] = file_selection
            self.module.command.statics[index][5] = file_selection_tag
            self.module.command.statics[index][6] = common_root
        
        self.builder.get_object('adjustment').set_upper(self.module.command.get_max_index())
        update_textview(self.builder.get_object('command_editor_textview'), 
                                                self.module.command,
                                                self.tagtable,
                                                get_spinner_index(self.builder.get_object('index_spin_button')))
        static_option_editor.hide()
    
    def on_soe_view_file_selection_button_clicked(self, file_selection_viewer):
        # get file selection & file type from entry
        ftype = self.builder.get_object('soe_radio_file').get_active()
        if not ftype:
            ftype = False      
        fs = self.builder.get_object('soe_file_selection_entry').get_text()
        # CALL VALIDATION SUB HERE
        # !!! NOTE for file type selections, last char must not be /
        # !!! NOTE for directory type selections, last character must not be
        # wildcard *
        list_file_selection_contents(self.builder, self.project.vars, fs, ftype)
    
    def on_soe_view_common_root_selection_button_clicked(self, file_selection_viewer):
        # get file selection & file type from entry
        ftype = False      
        fs = self.builder.get_object('common_root_dir_entry').get_text()
        # CALL VALIDATION SUB HERE
        # !!! NOTE for file type selections, last char must not be /
        # !!! NOTE for directory type selections, last character must not be
        # wildcard *
        list_file_selection_contents(self.builder, self.project.vars, fs, ftype)
        
    ####################################
    """ Iter Option Editor Handlers"""
    ####################################
    
    def on_ioe_ok_button_clicked(self, iter_option_editor):
        flag = self.builder.get_object('ioe_flag_entry').get_text()
        file_type_selection = self.builder.get_object('ioe_radio_file').get_active()
        file_selection = self.builder.get_object('ioe_file_selection_entry').get_text()
        none_tag_selection = self.builder.get_object('ioe_radio_none').get_active()
        input_tag_selection = self.builder.get_object('ioe_radio_input').get_active()
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
        
        edit, index = self.edit_flag
        if not edit:
            self.module.command.iters.append([None,
                                            "iter",
                                            flag,
                                            file_selection_type,
                                            file_selection,
                                            file_selection_tag])
        else:
            self.module.command.iters[index][2] = flag
            self.module.command.iters[index][3] = file_selection_type
            self.module.command.iters[index][4] = file_selection
            self.module.command.iters[index][5] = file_selection_tag
        
        self.builder.get_object('adjustment').set_upper(self.module.command.get_max_index())
        update_textview(self.builder.get_object('command_editor_textview'), self.module.command, self.tagtable, get_spinner_index(self.builder.get_object('index_spin_button')))
        iter_option_editor.hide()
        
    def on_ioe_view_selection_button_clicked(self, file_selection_viewer):
        # get file selection & file type from entry
        ftype = self.builder.get_object('ioe_radio_file').get_active()
        if not ftype:
            ftype = False      
        fs = self.builder.get_object('ioe_file_selection_entry').get_text()
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
        self.tagtable = tagtable
        self.module = None
        self.variable = None
        self.stdout = ""      
    

