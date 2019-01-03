#!/usr/bin/env python

def serialize_treemodel(treemodel, project):
    project.vars = []
    treemodel.foreach(serialize_vm_treeview, project)

def serialize_vm_treeview(liststore, path, row, project):
    project.vars.append([liststore.get_value(row, 0), liststore.get_value(row, 1)])
        


