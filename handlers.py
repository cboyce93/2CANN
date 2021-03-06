#!/usr/bin/env python3

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

import os
from os.path import expanduser
import signal
from copy import deepcopy
import threading
import time

from lib.project import Project, open_project
from lib.module import Module
from lib.command import Command
from lib.loop import Loop
from lib.variable import Variable
from util.treeview import *
from util.validation import *
from util.command_editor import *
from util.file_selection import *
from util.loop_utils import *
from util.run import *

# activate debugger
import pdb

class Handler:

    ###################################
    """ Global Handlers """
    ###################################
    
    def exit(self, wrapper, data=None):
        wrapper.destroy()
        Gtk.main_quit()
    
    def quit_button(self, wrapper):
        # save changes dialog
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
    """ Project Editor Handlers """
    ###################################
    
    ###---------------------------###      
    ### Project Filemenu Handlers ###
    ###---------------------------###
    
    def on_new_project_activated(self, unsaved_changes_dialog):
        # check if project has unsaved changes.
        self.project.monitor()
        if self.project.unsaved_changes:
            # show message dialog
            unsaved_changes_dialog.show()
        else:
            # create new project object
            self.project = Project()
            # initialize the GUI
            self.__init_project()
            
    def on_unsaved_changes_dialog_response(self, unsaved_changes_dialog, response):
        """ Read user response, save project if yes, close if no """
        print(response)
    
    def on_open_project_clicked(self, open_dialog):
        """ Show open dialog so user can select project file """
        self.immport = False
        open_dialog.show()
        
    def on_od_open_clicked(self, open_dialog):
        """ unpickle file and return project object """
        # get the filename
        fn = open_dialog.get_filename()
        if fn == self.project.filename:
            # throw info dialog if user tries to open ocurrent project
            info_dialog = self.builder.get_object('info_dialog')
            info_dialog.set_markup("<b>Info</b>")
            info_dialog.format_secondary_markup("Project already open.")
            info_dialog.show()
        else:
            self.project = open_project(fn)
            if self.immport:
                for module in self.project.modules:
                    module.state = "Ready"
                self.project.working_directory = expanduser("~")
                self.project.logs = []
            self.__init_project()
            self.init_liststores()
            open_dialog.hide()
    
    def on_save_project_activated(self, save_dialog):
        """ Pop up save as dialog is project has yet to be saved """
        self.export = False
        if self.project.filename is None:
            save_dialog.set_title("Save Project As...")
            save_dialog.set_current_name(self.project.name)
            save_dialog.show()
        else:
            self.project.save()
    
    def on_save_project_as_activated(self, save_dialog):
        """ Pop up save as dialog """
        self.export = False
        save_dialog.set_title("Save Project As...")
        save_dialog.set_current_name(self.project.name)
        save_dialog.show()
    
    def on_sd_save_clicked(self, save_dialog):
        """ Save the project """
        fn = save_dialog.get_filename()
        if fn is None or fn.isspace():
            info_dialog = self.builder.get_object('info_dialog') 
            info_dialog.format_secondary_markup("Please enter a project name.")
            info_dialog.show()
        elif fn[-4:] == '.pro':
            self.project.filename = fn
            self.project.name = fn.rsplit("/",1)[1]
        else:
            self.project.filename = fn + '.pro'
            self.project.name = fn.rsplit("/",1)[1] + '.pro'
        if self.export:
            project = self.project
            project.logs = []
            for module in project.modules:
                module.state = "Ready"
            project.working_directory = expanduser("~")
            project.save()
        else:
            self.project.save()
            self.builder.get_object('pe_header').set_subtitle(self.project.name)
        save_dialog.hide()
    
    def on_directory_setup_activated(self, data=None):
        """ Launch the directory setup tool """
        pass
    
    def on_import_project_activated(self, open_dialog):
        """ Import project
        
        Clear all module states, set working directory to user's home directory
        """
        self.immport = True
        open_dialog.show()
    
    def on_export_project_activated(self, save_dialog):
        """ Export project
        
        Clear module states, set working directory to user's home directory
        then save the project """
        save_dialog.set_title("Export Project...")
        if self.project.filename is None:
            warning_dialog = self.builder.get_object('warning_dialog')
            warning_dialog.set_markup("<b>Warning</b>")
            warning_dialog.format_secondary_markup("Save project before exporting.")
            warning_dialog.show()
        else:
            self.export = True   
            save_dialog.set_current_name(self.project.filename.rsplit("/",1)[1])
            save_dialog.show()
    
    def on_quit_program_activated(self, data=None):
        """ Exit program, ask if unsaved changes should be saved """
        pass
    
    ###------------------###
    ### Toolbar Handlers ###
    ###------------------###
    
    def on_run_all_clicked(self, data=None):
        """ Run all modules from selected module """
        terminal = self.builder.get_object('file_selection_viewer')
        stop_button = self.builder.get_object('fsv_stop_button')
        stop_button.set_visible(True)
        textview = self.builder.get_object('file_selection_textview')
        self.builder.get_object('fsv_header').set_title('Run All')
        buff = self.builder.get_object('file_selection_buffer')
        # clear buffer so we start with empty terminal
        buff.set_text("",-1)
        # just shorten up
        prj_cwd = self.project.working_directory
        terminal.show()
        # create an empty dictionary
        # key - Module obj
        # val - array of commands associated with module
        to_run = {}
        for module in self.project.modules:
            cmds = generate_cmds(self.builder, self.project, module.command)
            to_run[module] = cmds
        # flag to tell us if a subprocess is active
        self.process_live = True
        # open up non-blocking thread
        thread = threading.Thread(target=self.execute_cmd, 
                                    args=(to_run, textview, buff, prj_cwd))
        thread.daemon = True
        # fire up the thread
        thread.start()
        # make a new log for this run
        self.date = self.get_date()
        self.log_run_liststore.append([self.date])
    
    def get_date(self):
        """ Return the date formatted as "YYYY/MM/DD@HH:MM:SS" """
        thetime = time.localtime()
        # format year/month/day@hour:min:sec
        year    = str(thetime.tm_year)
        month   = str(thetime.tm_mon)
        day     = str(thetime.tm_mday)
        hour    = str(thetime.tm_hour)
        mn      = str(thetime.tm_min)
        sec     = str(thetime.tm_sec)
        return str(year+"/"+month.zfill(2)+"/"+day.zfill(2)+"@"+hour.zfill(2)+
                    ":"+mn.zfill(2)+":"+sec.zfill(2))
    
    def on_view_terminal_clicked(self, file_selection_viewer):
        """ Show the terminal if a process is active """
        if self.process_live:
            file_selection_viewer.show()
        else:
            warning_dialog = self.builder.get_object('warning_dialog')
            warning_dialog.set_markup("<b>Warning</b>")
            warning_dialog.format_secondary_markup("No active processes.")
            warning_dialog.show()
            
    """ The following subroutines are associated with run all tool button """
    
    def execute_cmd(self, to_run, textview, buff, prj_cwd):
        """ Execute all cmds in module """
        # iterate through the dictionary
        count = 0
        for self.mod, cmds in to_run.items():
            # update the header
            self.builder.get_object('fsv_header').set_title('Running ' + self.mod.name)
            # iterate through the commands
            for i, cmd in enumerate(cmds):
                if self.process_live:
                    # give user some feedback on process
                    self.builder.get_object('fsv_header').set_subtitle("("+str(i+1)+" of "+str(len(cmds))+") "+ cmd)
                    self.cp = SP.Popen([cmd], stdout=SP.PIPE, stderr=SP.PIPE, shell=True, cwd=prj_cwd, preexec_fn=os.setsid)
                    # store the process id in Handler object so we can kill it
                    # if necessary
                    self.pid = self.cp.pid      
                    # poll till process terminates
                    GLib.timeout_add(500, update_terminal, (self.cp, textview, buff))
                    # wait for the thread to finish up
                    self.cp.wait()   
                else:
                    break
            # store log
            if count > 1:
                # get last end iter
                start = end
                discard, end = buff.get_bounds() 
            else:
                start, end = buff.get_bounds()
            self.mod.log = buff.get_text(start, end, -1) 
            if self.cp.returncode == 0:
                self.mod.state = "Process complete."
            elif (self.mod.state != "Process killed. See log for details." and
                not self.process_live):
                # terminated with error code 1 or more
                self.mod.state = "Unprocessed."
                self.mod.log = "No terminal output."
            elif self.mod.state != "Process killed. See log for details.":
                self.mod.state = "Process terminated with errors. See log for details."   
            self.mod.run_time = self.date
            self.log_mod_liststore.append([self.date, self.mod.name, self.mod.state, self.mod.log])
            self.project.logs.append([self.date, self.mod.name, self.mod.state, self.mod.log])
            count += 1
            
        # update the gui with new module states post run
        self.reset_module_states()
    
    def on_stop_process_clicked(self, cancel_process_dialog):
        """ Show cancel process dialog """
        cancel_process_dialog.set_markup("<b>Warning</b>")
        cancel_process_dialog.format_secondary_markup("Are you sure you want to cancel the process?")
        cancel_process_dialog.show()
    
    def on_cancel_process_dialog_response(self, cancel_process_dialog, response):
        """ kill the process if user says so """
        if response == -8: # this was the output
            os.killpg(os.getpgid(self.pid), signal.SIGTERM)  # Send the signal to all the process groups
            # no live processes anymore
            self.process_live = False
            self.builder.get_object('fsv_header').set_subtitle('Process killed.')
            self.mod.state = "Process killed. See log for details."
            self.cp.kill()
        cancel_process_dialog.hide()
    
    """ Back to toolbar handlers now... """
     
    def on_new_module_clicked(self, module_editor):
        # Create new Module object
        self.module = Module()
        self.edit_module = False
        self.builder.get_object('module_editor_header').set_title('New Module')
        # clear the entries
        self.builder.get_object('module_name_entry').set_text("")
        self.builder.get_object('module_url_entry').set_text("")
        self.builder.get_object('module_command_entry').set_text("")
        self.builder.get_object('mod_notes_buff').set_text("",-1)
        module_editor.show()
    
    def on_edit_module_clicked(self, module_editor):
        self.set_self_module()
        self.edit_module = True
        self.builder.get_object('module_editor_header').set_title('Edit Module')
        self.builder.get_object('module_name_entry').set_text(self.module.name)
        self.builder.get_object('module_url_entry').set_text(self.module.uri)
        self.builder.get_object('module_command_entry').set_text(self.module.command.str)
        self.builder.get_object('mod_notes_buff').set_text(self.module.notes)
        module_editor.show()
    
    def on_delete_module_clicked(self, message_dialog):
        self.set_self_module()
        message_dialog.set_markup("<b>Warning</b>")
        message_dialog.format_secondary_markup("Are you sure you want to delete " + self.module.name + ".mod?")
        message_dialog.show()
    
    def on_mess_dialog_response(self, message_dialog, response):
        if response == -8:
            # delete module
            self.project.modules.remove(self.module)
            self.pro_liststore.remove(self.pro_liststore_iter)
            self.reset_module_indices()
            self.set_self_module()
        message_dialog.hide()
    
    def on_open_module_ref_clicked(self, warning_dialog):
        self.set_self_module()
        Gtk.show_uri_on_window(None, self.module.uri, Gdk.CURRENT_TIME)
    
    def on_view_log_clicked(self, viewer):
        header = self.builder.get_object('fsv_header')
        buff = self.builder.get_object('file_selection_buffer')
        stop_button = self.builder.get_object('fsv_stop_button')
        stop_button.set_visible(False)
        model, iterr = self.builder.get_object('pro_ed_selection').get_selected()
        mod_name = model.get_value(iterr, 1)
        for module in self.project.modules:
            if mod_name == module.name: 
                header.set_title(module.name)
                header.set_subtitle(module.run_time)
                buff.set_text(module.log, -1)
                break
        viewer.show()  
    
    def on_move_up_clicked(self, data=None):
        """ Move selected module up one position in queue """
        self.set_self_module()
        iterr = self.pro_liststore_iter
        index = self.pro_liststore.get_value(iterr, 0)-1
        if index > 0:
            self.pro_liststore.swap(self.pro_liststore.iter_previous(iterr), iterr)
            self.project.modules.remove(self.module)
            self.project.modules.insert(index-1, self.module)
            # reset step indices
            self.reset_module_indices()
    
    def on_move_down_clicked(self, data=None):
        """ Move selected module down one position in queue """
        self.set_self_module()
        iterr = self.pro_liststore_iter
        index = self.pro_liststore.get_value(iterr, 0)-1
        if index < len(self.project.modules)-1:
            self.pro_liststore.swap(self.pro_liststore.iter_next(iterr), iterr)
            self.project.modules.remove(self.module)
            self.project.modules.insert(index+1, self.module)
            # reset step indices
            self.reset_module_indices()     
    
    def on_pro_manager_selection_changed(self, selection):
        model, iterr = selection.get_selected()
        self.pro_liststore_iter = iterr
        
    def set_self_module(self):
        if self.pro_liststore_iter is not None:
            index = self.pro_liststore.get_value(self.pro_liststore_iter, 0)-1          
            self.module = self.project.modules[index]
            # need to do this in case cancel gets pressed so we don't lose
            # reference even if selection is unchanged
            self.last_module = self.module
    
    def cancel_new_module(self, module_editor):
        if self.last_module is not None:
            self.module = self.last_module
        module_editor.hide()
        
    ###---------------------###
    ### Tools Menu Handlers ###
    ###---------------------###
    
    def on_variable_manager_activated(self, variable_manager):
        variable_manager.show()
    
    def on_view_logs_activated(self, log_viewer):
        log_viewer.show()
    
    def on_preferences_manager_activated(self, preferences_manager):
        preferences_manager.show()
    
    ###--------------------###
    ### Help Menu Handlers ###
    ###--------------------###
    
    def on_about_activated(self, about_dialog):
        about_dialog.show()

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
        self.builder.get_object('variable_editor').hide()
        variable_manager.hide()

    ###################################
    """ Log Viewer Handlers """
    ###################################
    
    def on_log_run_selection_changed(self, selection):
        self.log_filter.refilter()
    
    def on_log_mod_selection_changed(self, selection):      
        buff = self.builder.get_object('log_buff')
        model, iterr = selection.get_selected()
        if iterr is not None:
            mod_date = model.get_value(iterr, 0)
            mod_name = model.get_value(iterr, 1)
            for log in self.project.logs:
                if log[0] == mod_date and log[1] == mod_name:
                    buff.set_text(log[3],-1)
    
    def log_filter_func(self, model, iterr, data):
        selection = self.builder.get_object('log_run_selection')
        run_model, run_iterr = selection.get_selected()
        if run_iterr is not None:
            date = run_model.get_value(run_iterr, 0)
            mod_date = model.get_value(iterr, 0)
            if mod_date is not None:
                if date == mod_date:
                    return True
        else:
            return False
    
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
        serialize_treemodel(self.builder.get_object('vm_treeview').get_model(),
                            self.project)                     
        variable_editor.hide() 
    
    ###################################
    """ Module Editor Handlers"""
    ###################################
    
    def on_cmd_editor_clicked(self, command_editor):
        self.tempcmd = deepcopy(self.module.command)
        self.reset_loop_liststore()
        self.builder.get_object('index_spin_button').set_value(float(0))
        self.builder.get_object('adjustment').set_upper(self.tempcmd.get_max_index())
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
            if self.edit_module:
                self.module.name = name
                self.module.uri = uri
                self.module.notes = notes
                self.pro_liststore.set(self.pro_liststore_iter, [0,1,2],
                                          [self.module.step,
                                          self.module.name,
                                          self.module.state])
                # user feedback
                info_dialog = self.builder.get_object('info_dialog')
                info_dialog.set_markup("<b>Info</b>")
                info_dialog.format_secondary_markup(self.module.name + ".mod updated successfully.")
                info_dialog.show()
                module_editor.hide()
            else:
                # save state
                self.module.name = name
                self.module.uri = uri
                self.module.notes = notes
                self.module.step = len(self.project.modules)+1
                self.module.state = "Ready"
                iterr = self.pro_liststore.append([ self.module.step,
                                            self.module.name,
                                            self.module.state])
                self.project.modules.append(self.module)
                # user feedback
                info_dialog = self.builder.get_object('info_dialog')
                info_dialog.set_markup("<b>Info</b>")
                info_dialog.format_secondary_markup(self.module.name + ".mod created successfully.")
                info_dialog.show()
                module_editor.hide()
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
        self.edit_loop = False
        self.builder.get_object('le_var_entry').set_text("")
        self.builder.get_object('le_dir_selection_entry').set_text("")
        loop_editor.show()
    
    def ce_on_edit_loop_clicked(self, loop_editor):
        self.set_self_loop()
        if self.loop_liststore_iter is not None:
            self.edit_loop = True
            # get rid of '$' at front of var, it will get added when saved
            self.builder.get_object('le_var_entry').set_text(self.loop.var[1:])
            self.builder.get_object('le_dir_selection_entry').set_text(self.loop.dir_selection)
            loop_editor.show()
        else:
            info_dialog = self.builder.get_object('info_dialog')
            info_dialog.set_markup("<b>Info</b>")
            info_dialog.format_secondary_markup("You must add at least one loop before editing.")
            info_dialog.show()
            
    def ce_on_delete_loop_clicked(self, data=None):
        self.set_self_loop()
        if self.loop_liststore_iter is not None:
            self.loop_liststore.remove(self.loop_liststore_iter)
            self.tempcmd.loops.remove(self.loop)
            self.reset_loop_indices()
            self.set_self_loop()
        else:
            info_dialog = self.builder.get_object('info_dialog')
            info_dialog.set_markup("<b>Info</b>")
            info_dialog.format_secondary_markup("You must add at least one loop before deleting.")
            info_dialog.show()
        
    
    def ce_on_loop_directories_clicked(self, loop_viewer):
        self.builder.get_object('lv_header').set_title("Loop Directories")
        self.builder.get_object('lv_header').set_subtitle(self.module.name)
        view_loop_directories(self.builder, self.project, self.tempcmd.loops)
        loop_viewer.show()
    
    def ce_on_loop_file_sel_clicked(self, file_selection_viewer):
        buff = self.builder.get_object('file_selection_buffer')
        stop_button = self.builder.get_object('fsv_stop_button')
        stop_button.set_visible(False)
        buff.set_text(get_loop_file_selection(self.builder, 
                                                self.project,
                                                self.module,
                                                self.tempcmd), -1)
        file_selection_viewer.show()
    
    def ce_on_run_test_clicked(self, file_selection_viewer):
        self.mod = self.module  # make the kill function happy
        cmds = generate_cmds(self.builder, self.project, self.tempcmd)    
        terminal = file_selection_viewer
        textview = self.builder.get_object('file_selection_textview')
        stop_button = self.builder.get_object('fsv_stop_button')
        stop_button.set_visible(True)
        self.builder.get_object('fsv_header').set_title('Run Test')
        self.builder.get_object('fsv_header').set_subtitle(self.module.name)
        terminal.show()
        buff = self.builder.get_object('file_selection_buffer')
        # clear buffer
        buff.set_text("",-1)
        prj_cwd = self.project.working_directory
        self.process_live = True
        thread = threading.Thread(target=self.execute_test_cmd, args=(self.builder, cmds, textview, buff, prj_cwd))
        thread.daemon = True
        thread.start()
    
    def execute_test_cmd(self, builder, cmds, textview, buff, prj_cwd):
        self.builder.get_object('fsv_header').set_title('Running ' + self.module.name)
        for i, cmd in enumerate(cmds):
            if self.process_live:
                self.builder.get_object('fsv_header').set_subtitle("("+str(i+1)+" of "+str(len(cmds))+") "+ cmd)
                self.cp = SP.Popen([cmd], stdout=SP.PIPE, stderr=SP.PIPE, shell=True, cwd=prj_cwd, preexec_fn=os.setsid)   
                self.pid = self.cp.pid     
                # poll till process terminates
                GLib.timeout_add(500, update_terminal, (self.cp, textview, buff))
                self.cp.wait()
            else:
                break
                
    
    def on_loop_selection_changed(self, selection):
        model, iterr = selection.get_selected()
        self.loop_liststore_iter = iterr
    
    def set_self_loop(self):
        if self.loop_liststore_iter is not None:
            index = self.loop_liststore.get_value(self.loop_liststore_iter, 0)-1
            self.loop = self.tempcmd.loops[index]
    
    # # # # # # # # # # # # #
    
    def on_add_function_clicked(self, function_editor):
        if self.tempcmd.func[2] is not "":
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
        if index == self.tempcmd.func[0]:
            self.tempcmd.func = [None, None, ""]
        for i,flag in enumerate(self.tempcmd.flags):
            if index == flag[0]:
                self.tempcmd.flags.remove(flag)
        for i,static in enumerate(self.tempcmd.statics):
            if index == static[0]:
                self.tempcmd.statics.remove(static)
        for i,sett in enumerate(self.tempcmd.sets):
            if index == sett[0]:
                self.tempcmd.sets.remove(sett)
        update_textview(self.builder.get_object('command_editor_textview'), 
                                                self.tempcmd,
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
        
    def on_le_ok_button_clicked(self, loop_editor):
        var = self.builder.get_object('le_var_entry').get_text()
        dir_selection = self.builder.get_object('le_dir_selection_entry').get_text()
        valid, error = validate_loop(var, dir_selection)
        if valid:
            if self.edit_loop:
                self.loop.var = "$"+var
                self.loop.var_selection = get_local_var_value(dir_selection)
                self.loop.dir_selection = dir_selection
                self.loop_liststore.set(self.loop_liststore_iter,
                                        [1,2,3],
                                        ["$"+var,
                                        get_local_var_value(dir_selection),
                                        dir_selection])
            else:
                # add new loop
                loop_no = len(self.tempcmd.loops)+1
                self.loop = Loop(loop_no, "$"+var, get_local_var_value(dir_selection), dir_selection)
                iterr = self.loop_liststore.append([loop_no,
                                                    "$"+var,
                                                    get_local_var_value(dir_selection),
                                                    dir_selection])
                self.tempcmd.loops.append(self.loop)
            loop_editor.hide()
        else:
            warning_dialog = self.builder.get_object('warning_dialog')
            warning_dialog.set_markup("<b>Warning</b>")
            warning_dialog.format_secondary_markup(error)
            warning_dialog.show()
            
    
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
    
    def init_liststores(self):
        """ populate liststores with values from project object """
        self.variables_liststore.clear()
        self.pro_liststore.clear()
        self.loop_liststore.clear()
        for var in self.project.vars:
                self.variables_liststore.append([var[0], var[1]])
        for module in self.project.modules:
            iterr = self.pro_liststore.append([ module.step,
                                                module.name,
                                                module.state])
            for loop in module.command.loops:
                iterr = self.loop_liststore.append([loop.no,
                                                    loop.var,
                                                    loop.var_selection,
                                                    loop.dir_selection])
        last_date = None
        for log in self.project.logs:
            if log[0] != last_date:
                self.log_run_liststore.append([log[0]])
            self.log_mod_liststore.append([log[0],log[1],log[2],log[3]])
            last_date = log[0]
    
    def reset_loop_liststore(self):
        self.loop_liststore.clear()
        for i,loop in enumerate(self.tempcmd.loops):
            self.loop_liststore.append([loop.no,
                                        loop.var,
                                        loop.var_selection,
                                        loop.dir_selection])

    def reset_module_indices(self):
        module_iters = []
        curr = self.pro_liststore.get_iter_first()
        while curr is not None:
            module_iters.append(curr)
            curr = self.pro_liststore.iter_next(curr)
        for i,module in enumerate(self.project.modules):
            module.step = i+1
            self.pro_liststore.set(module_iters[i], [0], [i+1])
    
    def reset_module_states(self):
        module_iters = []
        curr = self.pro_liststore.get_iter_first()
        while curr is not None:
            module_iters.append(curr)
            curr = self.pro_liststore.iter_next(curr)
        for i,module in enumerate(self.project.modules):
            self.pro_liststore.set(module_iters[i], [2], [module.state])
    
    def reset_loop_indices(self):
        loop_iters = []
        curr = self.loop_liststore.get_iter_first()
        while curr is not None:
            loop_iters.append(curr)
            curr = self.loop_liststore.iter_next(curr)
        for i,loop in enumerate(self.tempcmd.loops):
            loop.no = i+1
            self.loop_liststore.set(loop_iters[i], [0], [i+1])
    
    def __unsaved_changes(self, data=None):
        """ Place asterisk to the right of project name in project editor
            subtitle if there are unsaved changes """
        # check for unsaved changes
        self.project.monitor()
        if self.project.unsaved_changes:
            self.builder.get_object('pe_header').set_subtitle(self.project.name+"*")
        else:
            self.builder.get_object('pe_header').set_subtitle(self.project.name)
        return True
            
    
    def __init_project(self):
        """ Initialize some parameters for a new project """
        self.module = None
        self.variable = None
        self.pro_liststore_iter = None
        self.loop_liststore_iter = None
        self.last_module = None
        self.builder.get_object('work_dir_chooser').set_filename(self.project.working_directory)
        self.builder.get_object('pe_header').set_subtitle(self.project.name)
        self.process_live = False
        self.pro_liststore.clear()
        self.loop_liststore.clear()
        self.lv_liststore.clear()
        self.log_run_liststore.clear()
        self.log_mod_liststore.clear()
    
    def __init__(self, project, builder, liststores, tagtable):
        self.project = project
        self.builder = builder
        self.variables_liststore = liststores[0]
        self.pro_liststore = liststores[1]
        self.loop_liststore = liststores[2]
        self.lv_liststore = liststores[3]
        self.log_run_liststore = liststores[4]
        self.log_mod_liststore = liststores[5]
        #Creating the filter, feeding it with the liststore model
        self.log_filter = self.log_mod_liststore.filter_new()
        #setting the filter function
        self.log_filter.set_visible_func(self.log_filter_func)
        self.builder.get_object('log_mod_treeview').set_model(self.log_filter)
        self.tagtable = tagtable
        self.__init_project()
        # timeout to check if project obj state has changed
        GLib.timeout_add(500, self.__unsaved_changes, ())  

