#!/usr/bin/env python3

import pickle
from os.path import expanduser

class Project:

    def restore_iters(self, module_iters, loop_iters):
        """ Restore GTK Iter references so treeviews behave """
        for i,module in enumerate(self.modules):
            module.iter = module_iters[i]
        for i,loop in enumerate(self.loops):
            loop.iter = loop_iters[j]

    def save(self):
        # create file object
        # remove GTK Iter references since pickle can't deal with them
        try:
            fo = open(self.filename , 'wb')
            pickle.dump(self, fo, protocol=pickle.DEFAULT_PROTOCOL)
            self.last_state = self
        except pickle.PicklingError:
            print(pickle.PicklingError)
    
    def monitor(self):
        curr = pickle.dumps(self, -1)
        last = pickle.dumps(self.last_state, -1)
        if curr != last:
            self.unsaved_changes =  True
        else:
            self.unsaved_changes = False
     
    def print(self):
        for module in self.modules:
            print(module.step, module.name)   
    
    def __init__(self):
        self.name = 'Untitled'
        self.filename = None
        self.vars = []
        self.modules = []
        self.working_directory = expanduser("~")
        self.lib_dir = None
        self.last_state = None
