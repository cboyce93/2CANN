#!/usr/bin/env python

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from lib.module import Module
from lib.command import Command
from util.validation import *
from util.command_editor import *

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
    
    """ Library Manager Toolbar Handlers """
    
    def on_new_module_clicked(self, module_editor):
        self.builder.get_object('module_editor_header').set_title('New Module')
        # clear the entries
        self.builder.get_object('module_category_search_entry').set_text("")
        self.builder.get_object('module_name_entry').set_text("")
        self.builder.get_object('module_author_entry').set_text("")
        self.builder.get_object('module_description_entry').set_text("")
        self.builder.get_object('module_url_entry').set_text("")
        # Create new Module object
        self.module = Module()
        module_editor.show()
    
    def on_editor_module_clicked(self, module_editor):
        self.builder.get_object('module_editor_header').set_title('Edit Module')
        module_editor.show()
        
    ###################################
    """ Module Editor Handlers"""
    ###################################
    
    def on_cmd_editor_clicked(self, command_editor):
        if self.module.command is None:
            self.module.command = Command()
        command_editor.show()
        
    def on_save_module_button_clicked(self, data=None):
        self.module.category = self.builder.get_object('module_category_search_entry').get_text()
        self.module.name = self.builder.get_object('module_name_entry').get_text()
        self.module.author = self.builder.get_object('module_author_entry').get_text()
        self.module.desc = self.builder.get_object('module_description_entry').get_text()
        self.module.url = self.builder.get_object('module_url_entry').get_text()
        #### need to add this after self.module.command = None 
        #pdb.set_trace()
        # validate
        valid, error_message = validate_module(self.module)
        if valid:
            self.module.save()
            info_dialog = self.builder.get_object('info_dialog')
            info_dialog.set_markup("<b>Info</b>")
            info_dialog.format_secondary_markup(self.module.name + ".mod saved successfully.")
            info_dialog.show()
            self.builder.get_object('module_editor').hide()     
        else:
            warning_dialog = self.builder.get_object('warning_dialog')
            warning_dialog.set_markup("<b>Warning</b>")
            warning_dialog.format_secondary_markup(error_message)
            warning_dialog.show()
            
    ##############################
    """ Command Editor Handlers"""
    ##############################   
    
    def on_index_spin_button_value_changed(self, index_spin_button):
        update_textview(self.builder.get_object('command_editor_textview'), self.module.command, self.tagtable, self.get_index())
        
        
    
    def on_add_function_clicked(self, function_editor):
        if self.module.command.func is None:
            function_editor.show()
        else:
            self.builder.get_object('function_editor_header').set_title('Edit Function')
            self.builder.get_object('function_editor_entry').set_text(self.module.command.func)
            function_editor.show()
    
    def on_add_flag_option_clicked(self, flag_option_editor):
        flag_option_editor.show()
        
    def on_add_static_option_clicked(self, static_option_editor):
        static_option_editor.show()
    
    def on_add_iter_option_clicked(self, iter_option_editor):
        iter_option_editor.show()
        
    ###################################
    """ Function Editor Handlers"""
    ###################################
    
    def on_fe_ok_button_clicked(self, function_editor):
        # !! NOTE need to do validation here
        self.module.command.func = self.builder.get_object('function_editor_entry').get_text()
        self.builder.get_object('adjustment').set_upper(self.module.command.get_max_index())
        update_textview(self.builder.get_object('command_editor_textview'), self.module.command, self.tagtable, self.get_index())
        function_editor.hide()
        
    ###################################
    """ Flag Option Editor Handlers"""
    ###################################
    
    def on_foe_ok_button_clicked(self, flag_option_editor):
        # !! NOTE need to do validation here
        flag = self.builder.get_object('foe_flag_entry').get_text()
        self.module.command.flags.append(flag)
        self.builder.get_object('adjustment').set_upper(self.module.command.get_max_index())
        update_textview(self.builder.get_object('command_editor_textview'), self.module.command, self.tagtable, self.get_index())
        flag_option_editor.hide()
        
    ####################################
    """ Static Option Editor Handlers"""
    ####################################
    
    def on_soe_ok_button_clicked(self, static_option_editor):
        flag = self.builder.get_object('soe_flag_entry').get_text()
        file_selection = self.builder.get_object('soe_file_selection_entry').get_text()
        none_tag_selection = self.builder.get_object('soe_radio_none').get_active()
        input_tag_selection = self.builder.get_object('soe_radio_input').get_active()
        output_tag_selection = self.builder.get_object('soe_radio_output').get_active()
        # !! NOTE need to do validation here 
        if none_tag_selection:
            file_selection_tag = 'none'
        elif input_tag_selection:
            file_selection_tag = 'input'
        else:
            file_selection_tag = 'output'
        common_root = self.soe_common_root
        print(common_root)
        self.module.command.statics.append([flag, file_selection, file_selection_tag, common_root])
        self.builder.get_object('adjustment').set_upper(self.module.command.get_max_index())
        update_textview(self.builder.get_object('command_editor_textview'), self.module.command, self.tagtable, self.get_index())
        static_option_editor.hide()
    
    def on_soe_file_chooser_selection_changed(self, file_chooser):
        self.soe_common_root = file_chooser.get_uri()
        print(self.soe_common_root)
    
    def __init__(self, builder, tagtable):
        self.builder = builder
        self.tagtable = tagtable
        self.soe_common_root = None
    
    def get_index(self):
        return self.builder.get_object('index_spin_button').get_value_as_int()


