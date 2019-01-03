#!/usr/bin/env python

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
        return variables_liststore
          
            
    def __init__(self):
        # Create new project
        project = Project('Untitled.pro')
        builder = Gtk.Builder.new_from_file('2CANN.glade')
        variables_liststore = self.__init_var_manager_treeview(builder.get_object('vm_treeview'))
        # build tag table for command editor Gtk.TextView
        tagtable = init_tagtable()
        builder.connect_signals(Handler(project, builder, variables_liststore, tagtable))
        self.window = builder.get_object('wrapper')
        self.window.show_all()

def main():
    Gtk.main()

if __name__ == "__main__":
    win = twoCANN()
    main()
