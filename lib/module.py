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

    def __ne__(self,o):
        if type(self) != type(o):
            return True
        if self.name != o.name:
            return True
        if self.uri != o.uri:
            return True
        if self.command != o.command:
            return True
        if self.notes != o.notes:
            return True
        if self.state != o.state:
            return True
        if self.log != o.log:
            return True
        if self.run_time != o.run_time:
            return True
        else:
            return False
