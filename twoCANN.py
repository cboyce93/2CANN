#!/usr/bin/env python3

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from handlers import Handler
from lib.project import Project
from util.command_editor import init_tagtable

class twoCANN:

    def __init_var_manager_treeview(self, treeview):
        variables_liststore = Gtk.ListStore(str, str)
        treeview.set_model(variables_liststore)
        for i, col_title in enumerate(["Name", "Val"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(col_title, renderer, text=i)
            column.set_sort_column_id(i)
            treeview.append_column(column)
        # FOR TEST
        return variables_liststore
        
    def __init_pro_manager_treeview(self, treeview):
        pro_liststore = Gtk.ListStore(int, str, str)
        treeview.set_model(pro_liststore)
        for i, col_title in enumerate(["Step", "Module Name", "State"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(col_title, renderer, text=i)
            treeview.append_column(column)
            if i == 1:
                column.set_min_width(100)   # min width for module name
        # FOR TEST
        return pro_liststore  
    
    def __init_loop_manager_treeview(self, treeview):
        loop_liststore = Gtk.ListStore(int, str, str, str)
        treeview.set_model(loop_liststore)
        for i, col_title in enumerate(["No.", "Var", "Value", "Directory Selection"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(col_title, renderer, text=i)
            treeview.append_column(column)
        # FOR TEST
        return loop_liststore
    
    def __init_loop_viewer_treeview(self, treeview):
        lv_liststore = Gtk.ListStore(str, str)
        treeview.set_model(lv_liststore)
        for i, col_title in enumerate(["Var Value", "Directory Selection"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(col_title, renderer, text=i)
            column.set_sort_column_id(i)
            treeview.append_column(column)
        # FOR TEST
        return lv_liststore
    
    def __init__(self):
        # Create new project object
        project = Project()
        # import Glade generated GUI
        builder = Gtk.Builder.new_from_file('2CANN.glade')
        # Setup treeviews and liststores
        variables_liststore = self.__init_var_manager_treeview(builder.get_object('vm_treeview'))
        pro_liststore = self.__init_pro_manager_treeview(builder.get_object('pro_treeview'))
        loop_liststore = self.__init_loop_manager_treeview(builder.get_object('loop_treeview'))
        loop_viewer_liststore = self.__init_loop_viewer_treeview(builder.get_object('loop_viewer_treeview'))
        liststores = (variables_liststore, pro_liststore, loop_liststore, loop_viewer_liststore)
        # build tag table for command editor Gtk.TextView for different
        # text styles
        tagtable = init_tagtable()
        # connect event handlers
        builder.connect_signals(Handler(project, builder, liststores, tagtable))
        # build GUI
        self.window = builder.get_object('wrapper')
        self.window.show_all()

def main():
    Gtk.main()

if __name__ == "__main__":
    win = twoCANN()
    main()
