#!/usr/bin/env python3

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

from copy import deepcopy

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
        self.edit = False
        self.builder.get_object('module_editor_header').set_title('New Module')
        # clear the entries
        self.builder.get_object('module_name_entry').set_text("")
        self.builder.get_object('module_url_entry').set_text("")
        self.builder.get_object('module_command_entry').set_text("")
        self.builder.get_object('mod_notes_buff').set_text("",-1)
        # Create new Module object
        self.module = Module()
        module_editor.show()
    
    def on_editor_module_clicked(self, module_editor):
        self.edit = True
        self.builder.get_object('module_editor_header').set_title('Edit Module')
        self.builder.get_object('module_name_entry').set_text(self.module.name)
        self.builder.get_object('module_url_entry').set_text(self.module.uri)
        self.builder.get_object('module_command_entry').set_text(self.module.command.str)
        self.builder.get_object('mod_notes_buff').set_text(self.module.notes)
        module_editor.show()
    
    def on_delete_module_clicked(self, message_dialog):
        message_dialog.set_markup("<b>Warning</b>")
        message_dialog.format_secondary_markup("Are you sure you want to delete " + self.module.name + ".mod?")
        message_dialog.show()
    
    def on_mess_dialog_response(self, message_dialog, response):
        if response == -8:
            # delete module
            self.modules.remove(self.module)
            self.pro_liststore.remove(self.current_pro_liststore_iter)
            self.reset_step_indices()
            self.step -= 1 
        message_dialog.hide()
    
    def on_open_module_ref_clicked(self, warning_dialog):
        Gtk.show_uri_on_window(None, self.module.uri, Gdk.CURRENT_TIME)
    
    def on_view_log_clicked(self, data=None):
        pass
    
    def on_move_up_clicked(self, data=None):
        """ Move selected module up one position in queue """
        iterr = self.current_pro_liststore_iter
        index = self.pro_liststore.get_value(iterr, 0)-1
        if index >= 0 and index < len(self.modules):
            self.pro_liststore.swap(self.modules[index-1].iter, iterr)
        self.modules.remove(self.module)
        self.modules.insert(index-1, self.module)
        # reset step indices
        self.reset_step_indices()
    
    def on_move_down_clicked(self, data=None):
        """ Move selected module down one position in queue """
        iterr = self.current_pro_liststore_iter
        index = self.pro_liststore.get_value(iterr, 0)-1
        if index >= 0 and index < len(self.modules):
            self.pro_liststore.swap(self.modules[index+1].iter, iterr)
        self.modules.remove(self.module)
        self.modules.insert(index+1, self.module)
        # reset step indices
        self.reset_step_indices()       
    
    def on_pro_manager_selection_changed(self, selection):
        model, iterr = selection.get_selected()
        self.current_pro_liststore_iter = iterr
        if iterr is not None:
            index = model.get_value(iterr, 0)-1
            self.module = self.modules[index]
        
        
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
    
    def on_lib_dir_chooser_file_set(self, file_chooser):
        self.project.lib_dir = file_chooser.get_filename()
    
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
        self.tempcmd = deepcopy(self.module.command)
        update_textview(self.builder.get_object('command_editor_textview'),
                                                self.tempcmd,
                                                self.tagtable,
                                                get_spinner_index(self.builder.get_object('index_spin_button')))
        command_editor.show()
        
    def on_new_module_ok_button_clicked(self, module_editor):
        name = self.builder.get_object('module_name_entry').get_text()
        state = "Ready"
        uri = self.builder.get_object('module_url_entry').get_text()
        buff = self.builder.get_object('mod_notes_buff')
        notes = buff.get_text(buff.get_start_iter(), buff.get_end_iter(), False)
       
        #valid, error_message = validate_module(self.module)
        if True:
            # save state
            self.module.name = name
            self.module.uri = uri
            self.module.notes = notes
            if self.edit:
                self.pro_liststore.set(self.current_pro_liststore_iter, [0,1,2],
                                          [self.module.step,
                                          self.module.name,
                                          "Ready"])
                # user feedback
                info_dialog = self.builder.get_object('info_dialog')
                info_dialog.set_markup("<b>Info</b>")
                info_dialog.format_secondary_markup(self.module.name + ".mod updated successfully.")
                info_dialog.show()
                module_editor.hide()
            else:
                self.module.step = self.step
                self.module.iter = self.pro_liststore.append([ self.module.step,
                                            self.module.name,
                                            "Ready"])
                self.modules.append(self.module)
                # user feedback
                info_dialog = self.builder.get_object('info_dialog')
                info_dialog.set_markup("<b>Info</b>")
                info_dialog.format_secondary_markup(self.module.name + ".mod created successfully.")
                info_dialog.show()
                module_editor.hide()     
                # increment step
                self.step+=1
        else:
            warning_dialog = self.builder.get_object('warning_dialog')
            warning_dialog.set_markup("<b>Warning</b>")
            warning_dialog.format_secondary_markup(error_message)
            warning_dialog.show()
            
    ##############################
    """ Command Editor Handlers"""
    ##############################   
    
    def on_index_spin_button_value_changed(self, index_spin_button):
        update_textview(self.builder.get_object('command_editor_textview'), 
                                                self.tempcmd,
                                                self.tagtable,
                                                get_spinner_index(self.builder.get_object('index_spin_button')))
    
    # # # Loop handlers # # #
    
    def ce_on_add_loop_clicked(self, loop_editor):
        self.builder.get_object('le_var_entry').set_text("")
        self.builder.get_object('le_dir_selection_entry').set_text("")
        loop_editor.show()
    
    def ce_on_loop_directories_clicked(self, loop_viewer):
        self.builder.get_object('lv_header').set_title("Loop Directories")
        self.builder.get_object('lv_header').set_subtitle(self.module.name)
        view_loop_directories(self.builder, self.project, self.tempcmd.loops)
        loop_viewer.show()
    
    def ce_on_loop_file_sel_clicked(self, file_selection_viewer):
        buff = self.builder.get_object('file_selection_buffer')
        buff.set_text(get_loop_file_selection(self.builder, 
                                                self.project,
                                                self.module), -1)
        file_selection_viewer.show()
    
    def ce_on_run_test_clicked(self, file_selection_viewer):
        run_test(self.builder, self.project, self.module)
    
    # # # # # # # # # # # # #
    
    def on_add_function_clicked(self, function_editor):
        if self.tempcmd.func[2] is "":
            function_editor.show()
        else:
            self.builder.get_object('function_editor_header').set_title('Edit Function')
            self.builder.get_object('function_editor_entry').set_text(self.tempcmd.func[2])
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
        self.builder.get_object('se_relative').set_active(True)
        self.builder.get_object('se_file_selection_entry').set_text("")
        set_option_editor.show()
        
    def on_ce_edit_button_clicked(self, data=None):
        index = get_spinner_index(self.builder.get_object('index_spin_button'))
        if index == self.tempcmd.func[0]:
            # Edit function
            self.builder.get_object('function_editor_header').set_title('Edit Function')
            self.builder.get_object('function_editor_entry').set_text(self.tempcmd.func[2])
            self.builder.get_object('function_editor').show()
            return
        for i,flag in enumerate(self.tempcmd.flags):
            if index == flag[0]:
                self.edit_flag = True, i
                self.builder.get_object('foe_header').set_title("Edit Flag Option")
                self.builder.get_object('foe_flag_entry').set_text(flag[2])
                self.builder.get_object('flag_option_editor').show()
                return
        for i,static in enumerate(self.tempcmd.statics):
            if index == static[0]:
                self.edit_flag = True, i
                self.builder.get_object('soe_header').set_title("Edit Static Option")
                self.builder.get_object('soe_flag_entry').set_text(static[2])
                self.builder.get_object('soe_static_arg_entry').set_text(static[3])
                self.builder.get_object('static_option_editor').show()
                return
        for i,sett in enumerate(self.tempcmd.sets):
            if index == sett[0]:
                self.edit_flag = True, i
                self.builder.get_object('se_header').set_title("Edit Set Option")
                self.builder.get_object('se_flag_entry').set_text(sett[2])
                if sett[3]: # relative path
                    self.builder.get_object('se_relative').set_active(True)
                else:
                    self.builder.get_object('se_absolute').set_active(True)   
                self.builder.get_object('se_file_selection_entry').set_text(sett[4])
                self.builder.get_object('set_option_editor').show()
                return
    
    def on_ce_del_button_clicked(self, data=None):
        index = get_spinner_index(self.builder.get_object('index_spin_button'))
        if index == self.self.tempcmd.func[0]:
            self.self.tempcmd.func = [None, None, ""]
        for i,flag in enumerate(self.tempcmd.flags):
            if index == flag[0]:
                self.self.tempcmd.flags.remove(flag)
        for i,static in enumerate(self.self.tempcmd.statics):
            if index == static[0]:
                self.self.tempcmd.statics.remove(static)
        for i,sett in enumerate(self.self.tempcmd.sets):
            if index == sett[0]:
                self.self.tempcmd.sets.remove(sett)
        update_textview(self.builder.get_object('command_editor_textview'), 
                                                self.self.tempcmd,
                                                self.tagtable,
                                                get_spinner_index(self.builder.get_object('index_spin_button')))
            
    def on_command_editor_delete_event(self, command_editor, data=None):
        buff = Gtk.TextBuffer.new()
        buff.set_text("", -1)
        self.builder.get_object('command_editor_textview').set_buffer(buff)
        self.builder.get_object('index_spin_button').set_value(float(0))
        command_editor.hide()
        return True
    
    def on_ce_ok_button_clicked(self, command_editor):
        module_command_entry = self.builder.get_object('module_command_entry')
        module_command_entry.set_text(self.tempcmd.str)
        self.module.command = self.tempcmd
        command_editor.hide()
    
    
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
        loop_no = len(self.self.tempcmd.loops)+1
        self.self.tempcmd.loops.append([loop_no,
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
        self.tempcmd.func = [None, "func", self.builder.get_object('function_editor_entry').get_text()]
        self.builder.get_object('adjustment').set_upper(self.tempcmd.get_max_index())
        update_textview(self.builder.get_object('command_editor_textview'),
                                                self.tempcmd,
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
            self.tempcmd.flags.append([None, "flag", flag])
        else:
            self.tempcmd.flags[index][2] = flag
        self.builder.get_object('adjustment').set_upper(self.tempcmd.get_max_index())
        update_textview(self.builder.get_object('command_editor_textview'), self.tempcmd, self.tagtable, get_spinner_index(self.builder.get_object('index_spin_button')))
        flag_option_editor.hide()
        
    ####################################
    """ Static Option Editor Handlers"""
    ####################################
    
    def on_soe_ok_button_clicked(self, static_option_editor):
        flag = self.builder.get_object('soe_flag_entry').get_text()
        static_arg = self.builder.get_object('soe_static_arg_entry').get_text()
        
        edit, index = self.edit_flag
        if not edit:
            self.tempcmd.statics.append([None, 
                                        "static", 
                                        flag,
                                        static_arg])
        else:
            self.tempcmd.statics[index][2] = flag
            self.tempcmd.statics[index][3] = static_arg
        
        self.builder.get_object('adjustment').set_upper(self.tempcmd.get_max_index())
        update_textview(self.builder.get_object('command_editor_textview'), 
                                                self.tempcmd,
                                                self.tagtable,
                                                get_spinner_index(self.builder.get_object('index_spin_button')))
        static_option_editor.hide()

    ####################################
    """ Set Option Editor Handlers"""
    ####################################
    
    def on_se_ok_button_clicked(self, set_option_editor):
        flag = self.builder.get_object('se_flag_entry').get_text()
        set_type = self.builder.get_object('se_relative').get_active()
        file_selection = self.builder.get_object('se_file_selection_entry').get_text()

        # !! NOTE need to do validation here 
        if set_type:
            relative = True
        else:
            relative = False
        
        edit, index = self.edit_flag
        if not edit:
            self.tempcmd.sets.append([None,
                                            "iter",
                                            flag,
                                            relative,
                                            file_selection])
        else:
            self.tempcmd.sets[index][2] = flag
            self.tempcmd.sets[index][3] = relative
            self.tempcmd.sets[index][4] = file_selection
            
        
        self.builder.get_object('adjustment').set_upper(self.tempcmd.get_max_index())
        update_textview(self.builder.get_object('command_editor_textview'), 
                                                self.tempcmd,
                                                self.tagtable,
                                                get_spinner_index(self.builder.get_object('index_spin_button')))
        set_option_editor.hide()
    
    ######################################
    """ File Selection Viewer Handlers"""
    ######################################
    
    #handlers go here
    
    ######################################
    
    def reset_step_indices(self):
        for i,module in enumerate(self.modules):
            module.step = i+1
            self.pro_liststore.set(module.iter, [0], [i+1])
    
    def __init__(self, project, builder, liststores, tagtable):
        self.project = project
        self.builder = builder
        self.variables_liststore = liststores[0]
        self.pro_liststore = liststores[1]
        self.modules = []
        self.loop_liststore = liststores[2]
        self.lv_liststore = liststores[3]
        self.tagtable = tagtable
        self.module = None
        self.variable = None
        self.stdout = ""
        self.step = 1

        """
        # # # TEST CASE 1
        self.project.vars.append(["${ROOT}", "ASD/TD"])
        self.project.working_directory = "/home/cboyce/Documents/"
        self.module = Module()
        self.loop_liststore.append([1, "$subj", "%{(SUB..)}", "${ROOT}/<v>%{(SUB..)}</v>"])
        self.loop_liststore.append([2, "$run", "%{(RUN..)}", "/*/<v>%{(RUN..)}</v>"])
        self.module.command.loops.append([1, "$subj", "%{(SUB..)}", "${ROOT}/<v>%{(SUB..)}</v>"])
        self.module.command.loops.append([2, "$run", "%{(RUN..)}", "/*/<v>%{(RUN..)}</v>"])
        
        self.module.command.func = [None, "func", "3dDespike"]
        self.module.command.sets.append([None, "iter", "-prefix", True, "d.{$subj}.REST.{$run}+orig"])
        self.module.command.sets.append([None, "iter", "", True, "{$subj}.REST.{$run}+orig"])
        """
              
    

