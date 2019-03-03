#!/usr/bin/env python328

import pickle
from os.path import expanduser
import difflib
import copy

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
            x = copy.deepcopy(self)
            #pdb.set_trace()
            self.last_state = copy.deepcopy(x) # make a copy of object in mem
            #print("Hello" + str(self != self.last_state))
        except pickle.PicklingError:
            print(pickle.PicklingError)

    def monitor(self):
        """ Let 2CANN know if there are unsaved changes """
        #print("Monitor: " + str(self != self.last_state)) #used for debugging

        if self != self.last_state:
            self.unsaved_changes =  True
        else:
            self.unsaved_changes = False

    def __init__(self):
        self.name = 'Untitled.pro'
        self.filename = 'Untitled.pro'
        self.vars = []
        self.modules = []
        self.logs = []
        self.working_directory = expanduser("~")
        self.unsaved_changes = False
        self.last_state = copy.deepcopy(self)

    def __ne__(self,o):

        if self.name != o.name:
            return True

        if self.filename != o.filename:
            return True

        # check if variables are the same
        if len(self.vars) != len(o.vars):
            return True
        else:
            for i in range(len(self.vars)):
                if self.vars[i] != o.vars[i]:
                    return True

        # check if modules are the same
        if len(self.modules) != len(o.modules):
            return True
        else:
            for i in range(len(self.modules)):
                if self.modules[i] != o.modules[i]:
                    return True

        # check if the logs are the are same
        if len(self.logs) != len(o.logs):
            return True
        if len(self.logs) == len(o.logs):
            for i in range(len(self.logs)):
                if self.logs[i] != o.logs[i]:
                    return True
        else:
            return False
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
