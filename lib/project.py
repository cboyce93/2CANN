#!/usr/bin/env python328

import pickle
from os.path import expanduser
import difflib
from copy import deepcopy

import pdb

class Project:

    def restore_iters(self, module_iters, loop_iters):
        """ Restore GTK Iter references so treeviews behave """
        for i,module in enumerate(self.modules):
            module.iter = module_iters[i]
        for i,loop in enumerate(self.loops):
            loop.iter = loop_iters[j]

    def save(self):
        """ Save to file """
        try:
            fo = open(self.filename , 'wb')
            pickle.dump(self, fo, protocol=pickle.DEFAULT_PROTOCOL)
            self.last_state = deepcopy(self) # make a copy of object in mem
        except pickle.PicklingError:
            print(pickle.PicklingError)
    
    def monitor(self):
        """ Let 2CANN know if there are unsaved changes """
        if self != self.last_state:
            self.unsaved_changes =  True
        else:
            self.unsaved_changes = False 
 
    def __init__(self):
        self.name = 'Untitled.pro'
        self.filename = None
        self.vars = []
        self.modules = []
        self.working_directory = expanduser("~")
        self.last_state = self
        self.unsaved_changes = False
    
    def __ne__(self,o):
        pass
        """ Return True if project objects not equal, fasle if equal.
        
        Write a method to compare projects. You will have to write an
        __ne__ or __eq__ method for both Module and Command Objects as well
        which this function should call. I recommend iterating through the 
        modules and vars since once you deepcopy you have to evaluate by value
        since refs have changed. """

def open_project(filename):
    """ Open project from file and return project obj """
    try:
        fo = open(filename, 'rb')
        return pickle.load(fo)
    except pickle.UnpicklingError:
        pass
