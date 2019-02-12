#!/usr/bin/env python3

from lib.command import Command
import pickle

class Module:
    
    def __init__(self):
        self.name = "unsaved"
        self.uri = None
        self.command = Command()
        self.notes = None
        self.state = None
        self.log = None
        self.run_time = None

        
