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
        variables_liststore.append(["${ROOT}", "/home/cboyce/git/2CANN"])
        return variables_liststore
        
    def __init_lib_manager_treeview(self, treeview):
        lib_liststore = Gtk.ListStore(str, str, str, str, str)
        treeview.set_model(lib_liststore)
        for i, col_title in enumerate(["Category", "Name", "Author", "Description", "Filepath"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(col_title, renderer, text=i)
            column.set_sort_column_id(i)
            treeview.append_column(column)
            if i == 4:
                column.set_visible(False)
        # FOR TEST
        return lib_liststore  
            
    def __init__(self):
        # Create new project object
        project = Project('Untitled.pro')
        # import Glade generated GUI
        builder = Gtk.Builder.new_from_file('2CANN.glade')
        # Setup treeviews and liststores
        variables_liststore = self.__init_var_manager_treeview(builder.get_object('vm_treeview'))
        lib_liststore = self.__init_lib_manager_treeview(builder.get_object('lib_treeview'))
        liststores = (variables_liststore, lib_liststore)
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
