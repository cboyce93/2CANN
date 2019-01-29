#!/usr/bin/env python3

from lib.command import Command
import pickle

class Module:

    def save(self, root_dir):
        # create file object
        try:
            self.set_filepath(root_dir)
            fo = open(self.fp , 'wb')
            pickle.dump(self, fo, protocol=pickle.DEFAULT_PROTOCOL)
        except pickle.PicklingError:
            pass

    def set_filepath(self, root):
        self.fp = root + self.name + ".mod"
    
    def __init__(self):
        self.name = "unsaved"
        self.uri = None
        self.command = Command()
        self.notes = None

        
