import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class Handler:

    ##############################
    """ Global Handlers """
    ##############################
    
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
        
    ##############################
    """ Main Window Handlers """
    ##############################
            
    """ File Menu Handlers """
    
    """ Tools Menu Handlers """
    
    def on_variable_manager_activated(self, variable_manager):
        variable_manager.show()
    
    """ Help Menu Handlers """
    
    def on_about_activated(self, about_dialog):
        about_dialog.show()
        
    """ Pipeline Editor Toolbar Handlers """
    
    """ Library Manager Toolbar Handlers """
    
    def on_new_module_clicked(self, module_editor):
        self.builder.get_object('module_editor_header').set_title('New Module')
        module_editor.show()
    
    def on_editor_module_clicked(self, module_editor):
        self.builder.get_object('module_editor_header').set_title('Edit Module')
        module_editor.show()
        
    ##############################
    """ Module Editor Handlers"""
    ############################## 
    
    def on_cmd_editor_clicked(self, command_editor):
        command_editor.show()
        
    ##############################
    """ Command Editor Handlers"""
    ##############################   
    
    
    def on_add_function_clicked(self, function_editor):
        function_editor.show()
    
    def on_add_flag_option_clicked(self, flag_option_editor):
        flag_option_editor.show()
        
    def on_add_static_option_clicked(self, static_option_editor):
        static_option_editor.show()
    
    def on_add_iter_option_clicked(self, iter_option_editor):
        iter_option_editor.show()
        
    
        
    
    def __init__(self, builder):
        self.builder = builder


